from typing import List
import re

from langchain_core.messages import AIMessage

from downes.model import call_llm
from downes.prompts import (
    ACTION_SYSTEM_PROMPT,
    get_answer_system_prompt,
    PLANNING_SYSTEM_PROMPT,
    get_tool_args_system_prompt,
    VALIDATION_SYSTEM_PROMPT,
    META_VALIDATION_SYSTEM_PROMPT,
)
from downes.tools import TOOLS
from downes.utils.logger import Logger
from downes.utils.ui import show_progress
from downes.utils.vault import Vault


class Task:
    """Simple task representation - no Pydantic complexity"""

    def __init__(self, id: int, description: str, done: bool = False):
        self.id = id
        self.description = description
        self.done = done

    def dict(self):
        return {"id": self.id, "description": self.description, "done": self.done}


class Agent:
    def __init__(this, max_steps: int = 20, max_steps_per_task: int = 5, verbose: bool = False, debug: bool = False):
        this.logger = Logger(verbose=verbose)
        this.max_steps = max_steps  # global safety cap
        this.max_steps_per_task = max_steps_per_task
        this.vault = Vault()
        this.verbose = verbose
        this.debug = debug

    # ---------- helper methods ----------
    @staticmethod
    def _extract_content(response) -> str:
        """Extract text content from LLM response."""
        return response.content if hasattr(response, "content") else str(response)

    @staticmethod
    def _is_affirmative(text: str) -> bool:
        """Check if text starts with yes/affirmative response."""
        return text.strip().lower().startswith("yes")

    @staticmethod
    def _normalize_arg_value(value):
        """Convert stringified lists to actual lists."""
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            try:
                import json, ast

                try:
                    parsed = json.loads(value)
                except Exception:
                    parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return value

    def _call_llm_safe(
        this,
        prompt: str,
        system_prompt: str,
        tools=None,
        error_msg: str = "LLM call failed",
        operation_name: str = "LLM call",
    ):
        """Call LLM with error handling and logging."""
        if this.debug:
            this.logger._log(f"\n{'='*60}\n[DEBUG] {operation_name}")
            this.logger._log(f"[SYSTEM PROMPT]\n{system_prompt[:200]}...\n")
            this.logger._log(f"[USER PROMPT]\n{prompt[:500]}...\n")
        
        try:
            response = call_llm(
                prompt, 
                system_prompt=system_prompt, 
                tools=tools,
                verbose=this.verbose or this.debug
            )
            
            if this.debug and response:
                content = this._extract_content(response)
                this.logger._log(f"[RESPONSE]\n{content[:500]}...")
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    this.logger._log(f"[TOOL CALLS] {len(response.tool_calls)} call(s)")
                this.logger._log(f"{'='*60}\n")
            
            return response
        except Exception as e:
            this.logger._log(f"{error_msg}: {e}")
            return None

    def _mark_task_done(this, task: Task):
        """Mark a task as complete and log it."""
        task.done = True
        this.logger.log_task_done(task.description)

    def _check_step_limit(this, step_count: int, context: str = "Global") -> bool:
        """Check if step limit is reached and log if so."""
        if step_count >= this.max_steps:
            this.logger._log(
                f"{context} max steps reached — aborting to avoid runaway loop."
            )
            return True
        return False

    def _format_output(
        this, tool_name: str, args: dict, result_or_error, is_error: bool = False
    ) -> str:
        """Format tool execution output or error message."""
        prefix = "Error from" if is_error else "Output of"
        return f"{prefix} {tool_name} with args {args}: {result_or_error}"

    def _detect_loop(this, last_actions: list, action_sig: str) -> bool:
        """Detect if we're stuck in a repeating action loop."""
        last_actions.append(action_sig)
        if len(last_actions) > 4:
            last_actions[:] = last_actions[-4:]  # Modify in place

        if len(set(last_actions)) == 1 and len(last_actions) == 4:
            this.logger._log("Detected repeating action — aborting to avoid loop.")
            return True
        return False

    # ---------- task planning ----------
    def plan_tasks(this, query: str) -> List[Task]:
        """Plan tasks for the given query with progress indication."""
        @show_progress("Planning tasks...", "Tasks planned", enabled=not this.debug)
        def _do_plan():
            return this._plan_tasks_impl(query)
        return _do_plan()
    
    def _plan_tasks_impl(this, query: str) -> List[Task]:
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in TOOLS])
        prompt = f"""
        Given the user query: "{query}",
        Create a list of curriculum development tasks to be completed.
        Return tasks as a Markdown checklist.
        Keep tasks atomic and aligned to available tools.
        """
        system_prompt = PLANNING_SYSTEM_PROMPT.format(tools=tool_descriptions)

        def _parse_markdown_checklist(text: str) -> List[Task]:
            """Parse a Markdown checklist into Task objects"""
            tasks = []
            # Match checklist items: - [ ] Task description
            pattern = r"-\s*\[\s*\]\s*(.+?)(?=\n-\s*\[|$)"
            matches = re.findall(pattern, text, re.DOTALL)

            for idx, match in enumerate(matches, start=1):
                description = match.strip()
                if description and not description.startswith("(none"):
                    tasks.append(Task(id=idx, description=description, done=False))

            return tasks

        response = this._call_llm_safe(
            prompt, system_prompt, error_msg="Planning failed", operation_name="Task Planning"
        )
        if response:
            tasks = _parse_markdown_checklist(this._extract_content(response))

        if not response or not tasks:
            # Retry once with a clarified prompt
            retry_prompt = f"""
            The user's request may contain typos or be ambiguous.
            First, rewrite it as a clear curriculum-development request with topic, audience, and level if implied.
            Then produce a Markdown checklist with 3-6 atomic tasks aligned to available tools.

            Original request: "{query}"
            """
            response = this._call_llm_safe(
                retry_prompt, system_prompt, error_msg="Planning retry failed", operation_name="Task Planning (Retry)"
            )
            tasks = (
                _parse_markdown_checklist(this._extract_content(response))
                if response
                else []
            )

            if not tasks:
                tasks = [Task(id=1, description=query, done=False)]

        task_dicts = [task.dict() for task in tasks]
        this.logger.log_task_list(task_dicts)
        return tasks

    # ---------- ask Model what to do ----------
    def plan_next_actions(this, task_desc: str, last_outputs: str = "") -> AIMessage:
        """Plan next actions with conditional progress display."""
        @show_progress("Thinking...", "", enabled=not this.debug)
        def _do_plan():
            return this._plan_next_actions_impl(task_desc, last_outputs)
        return _do_plan()
    
    def _plan_next_actions_impl(this, task_desc: str, last_outputs: str = "") -> AIMessage:
        # last_outputs = textual feedback of what we just tried
        prompt = f"""
        We are working on: "{task_desc}".
        
        Last tool outputs: 
        ```
        {last_outputs}
        ```

        Given the task and the outputs, our next step is to:
        """
        response = this._call_llm_safe(
            prompt,
            ACTION_SYSTEM_PROMPT,
            tools=TOOLS,
            error_msg="plan_next_actions failed",
            operation_name="Action Planning",
        )
        return response if response else AIMessage(content="Failed to get actions.")

    def ask_if_done(this, task_desc: str, recent_results: str) -> bool:
        """Check if task is done with conditional progress display."""
        @show_progress("Checking if task is complete...", "", enabled=not this.debug)
        def _do_check():
            return this._ask_if_done_impl(task_desc, recent_results)
        return _do_check()
    
    def _ask_if_done_impl(this, task_desc: str, recent_results: str) -> bool:
        prompt = f"""
        We are trying to complete task: "{task_desc}".
        Given the history of tool outputs so far: {recent_results}

        Is the task done?
        """
        response = this._call_llm_safe(
            prompt, VALIDATION_SYSTEM_PROMPT, error_msg="Task validation failed", operation_name="Task Validation"
        )
        return (
            this._is_affirmative(this._extract_content(response)) if response else False
        )

    def is_goal_achieved(this, query: str, task_outputs: list) -> bool:
        """Check if goal is achieved with conditional progress display."""
        @show_progress("Checking if main goal is achieved...", "", enabled=not this.debug)
        def _do_check():
            return this._is_goal_achieved_impl(query, task_outputs)
        return _do_check()
    
    def _is_goal_achieved_impl(this, query: str, task_outputs: list) -> bool:
        """Check if the overall goal is achieved based on all session outputs."""
        all_results = "\n\n".join(task_outputs)
        prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools so far:
        {all_results}
        
        Based on the data above, is the original query answered well?
        """
        response = this._call_llm_safe(
            prompt, META_VALIDATION_SYSTEM_PROMPT, error_msg="Meta-validation failed", operation_name="Goal Validation"
        )
        return (
            this._is_affirmative(this._extract_content(response)) if response else False
        )

    def optimize_tool_args(
        this, tool_name: str, initial_args: dict, task_desc: str
    ) -> dict:
        """Optimize tool args with conditional progress display."""
        @show_progress("Optimizing tool call...", "", enabled=not this.debug)
        def _do_optimize():
            return this._optimize_tool_args_impl(tool_name, initial_args, task_desc)
        return _do_optimize()
    
    def _optimize_tool_args_impl(
        this, tool_name: str, initial_args: dict, task_desc: str
    ) -> dict:
        """Optimize tool arguments based on task requirements."""
        tool = next((t for t in TOOLS if t.name == tool_name), None)
        if not tool:
            return initial_args

        # Get tool schema info
        tool_description = tool.description
        tool_schema = (
            tool.args_schema.schema()
            if hasattr(tool, "args_schema") and tool.args_schema
            else {}
        )

        prompt = f"""
        Task: "{task_desc}"
        Tool: {tool_name}
        Tool Description: {tool_description}
        Tool Parameters: {tool_schema}
        Initial Arguments: {initial_args}
        
        Given the task, optimize the arguments to ensure all relevant parameters are used correctly.
        *Note:Pay special attention to filtering parameters that would help narrow down results to match the task.*
        """
        response = this._call_llm_safe(
            prompt,
            get_tool_args_system_prompt(),
            error_msg="Argument optimization failed",
            operation_name="Argument Optimization",
        )
        if response:
            content = this._extract_content(response)

            # Parse simple key-value format from Markdown code block
            optimized = {}
            # Look for code block first
            code_block_match = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1)

            # Parse key: value pairs
            for line in content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Try to parse value as Python literal (handles lists, numbers, bools)
                    try:
                        import ast

                        optimized[key] = ast.literal_eval(value)
                    except:
                        # Keep as string if parsing fails
                        optimized[key] = value

            # Merge with initial args (optimized takes precedence)
            return {**initial_args, **optimized} if optimized else initial_args
        else:
            return initial_args

    def _execute_tool(this, tool, tool_name: str, inp_args):
        """Execute a tool with progress indication."""
        @show_progress(f"Executing {tool_name}...", "", enabled=not this.debug)
        def run_tool():
            if this.debug:
                this.logger._log(f"[TOOL EXECUTION] {tool_name} with args: {inp_args}")
            result = tool.run(inp_args)
            if this.debug:
                result_preview = str(result)[:200] if result else "None"
                this.logger._log(f"[TOOL RESULT] {result_preview}...")
            return result
        return run_tool()

    def confirm_action(this, tool: str, input_str: str) -> bool:
        """
        Confirm whether to execute a given action.

        In a production environment, this would prompt the user for confirmation.
        For this example, we log and auto-confirm. Risky tools are not
        implemented in this version.
        """
        # TODO logging
        # logging.info(f"CONFIRMING ACTION: Tool={tool}, Input='{input_str}'")
        return True

    def run(this, query: str):
        """
        Executes the main agent loop to process a user query.

        This method orchestrates the entire process of understanding a query,
        planning tasks, executing tools to gather information, and synthesizing
        a final answer.

        Args:
            query (str): The user's natural language query.

        Returns:
            str: A comprehensive answer to the user's query.
        """
        # Display the user's query
        this.logger.log_user_query(query)

        # Create a directory for this run
        this.vault.create_run_dir(query)

        # Initialize agent state for this run.
        step_count = 0
        last_actions = []
        task_outputs = []  # outputs from all tasks

        # 1. Decompose the user query into a list of tasks.
        tasks = this.plan_tasks(query)

        # If no tasks were created, the query is likely out of scope.
        if not tasks:
            answer = this._generate_answer(query, task_outputs)
            this.logger.log_summary(answer)
            return answer

        # 2. Loop through tasks until all tasks are complete or the max steps are reached.
        while any(not task.done for task in tasks):
            # Global safety break.
            if this._check_step_limit(step_count, "Global"):
                break

            # Select the next incomplete task.
            task = next(task for task in tasks if not task.done)
            this.logger.log_task_start(task.description)

            # Define per-task state.
            per_task_steps = 0
            task_step_outputs = []  # outputs from a single step of a given task.

            # Loop through steps of a single task until the task is complete or the max steps are reached.
            while per_task_steps < this.max_steps_per_task:
                if this._check_step_limit(step_count, "Global"):
                    return

                # Ask the LLM for the next action to take for the current task.
                ai_message = this.plan_next_actions(
                    task.description, last_outputs="\n".join(task_step_outputs)
                )

                # If no tool is called, the task is considered complete.
                if not ai_message.tool_calls:
                    this._mark_task_done(task)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    if step_count >= this.max_steps:
                        break

                    tool_name = tool_call["name"]
                    initial_args = tool_call["args"]

                    # Basic arg normalization: convert stringified lists to real lists
                    initial_args = {
                        k: this._normalize_arg_value(v) for k, v in initial_args.items()
                    }

                    # Refine tool arguments for better performance.
                    optimized_args = this.optimize_tool_args(
                        tool_name, initial_args, task.description
                    )

                    # Detect and prevent repetitive action loops.
                    action_sig = f"{tool_name}:{optimized_args}"
                    if this._detect_loop(last_actions, action_sig):
                        return

                    # Execute the tool.
                    tool_to_run = next((t for t in TOOLS if t.name == tool_name), None)
                    if tool_to_run and this.confirm_action(
                        tool_name, str(optimized_args)
                    ):
                        try:
                            result = this._execute_tool(
                                tool_to_run, tool_name, optimized_args
                            )
                            this.logger.log_tool_run(optimized_args, result)
                            this.vault.save_artifact(
                                task_name=task.description,
                                artifact_name=tool_name,
                                content=result,
                            )
                            output = this._format_output(
                                tool_name, optimized_args, result
                            )
                            task_outputs.append(output)
                            task_step_outputs.append(output)
                        except Exception as e:
                            this.logger._log(f"Tool execution failed: {e}")
                            error_output = this._format_output(
                                tool_name, optimized_args, e, is_error=True
                            )
                            task_outputs.append(error_output)
                            task_step_outputs.append(error_output)
                    else:
                        this.logger._log(f"Invalid tool: {tool_name}")

                    step_count += 1
                    per_task_steps += 1

                # Task-level introspection: Check if the task is complete.
                if this.ask_if_done(task.description, "\n".join(task_step_outputs)):
                    this._mark_task_done(task)
                    break

            # Global introspection: Check if the overall goal is achieved.
            if task.done and this.is_goal_achieved(query, task_outputs):
                this.logger._log("Main goal achieved. Finalizing answer.")
                break

        # Generate the final answer from all collected tool outputs.
        answer = this._generate_answer(query, task_outputs)
        this.logger.log_summary(answer)
        this.vault.save_artifact("summary", "final_answer", answer)
        return answer

    def _generate_answer(this, query: str, task_outputs: list) -> str:
        """Generate answer with conditional progress display."""
        @show_progress("Generating answer...", "Answer ready", enabled=not this.debug)
        def _do_generate():
            return this._generate_answer_impl(query, task_outputs)
        return _do_generate()
    
    def _generate_answer_impl(this, query: str, task_outputs: list) -> str:
        """Generate the final answer based on collected data."""
        all_results = (
            "\n\n".join(task_outputs) if task_outputs else "No data was collected."
        )
        answer_prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools:
        {all_results}
        
        Based on the data above, provide a comprehensive answer to the user's query.
        Organize the output for curriculum use: summary, objectives, modules, assessments, pacing, resources (if any).
        """
        response = this._call_llm_safe(
            answer_prompt,
            get_answer_system_prompt(),
            error_msg="Answer generation failed, using fallback",
            operation_name="Answer Generation",
        )
        if response:
            content = this._extract_content(response)
            if content:
                return content

        # Fallback: return a synthesized summary from collected outputs
        fallback = [
            "# Summary",
            "",
            f"**Query:** {query}",
            f"**Outputs Collected:** {len(task_outputs)}",
            "",
            "## Key Outputs",
            "",
        ]
        fallback.extend([f"- {o[:200]}..." for o in task_outputs[-5:]])
        return "\n".join(fallback)
