from typing import List

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
from downes.schemas import Answer, IsDone, OptimizedToolArgs, Task, TaskList
from downes.tools import TOOLS
from downes.utils.logger import Logger
from downes.utils.ui import show_progress
from downes.utils.vault import Vault


class Agent:
    def __init__(this, max_steps: int = 20, max_steps_per_task: int = 5):
        this.logger = Logger()
        this.max_steps = max_steps  # global safety cap
        this.max_steps_per_task = max_steps_per_task
        this.vault = Vault()

    # ---------- task planning ----------
    @show_progress("Planning tasks...", "Tasks planned")
    def plan_tasks(this, query: str) -> List[Task]:
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in TOOLS])
        prompt = f"""
        Given the user query: "{query}",
        Create a list of curriculum development tasks to be completed.
        Return a JSON object: {{"tasks": [{{"id": 1, "description": "some task", "done": false}}]}}
        Keep tasks atomic and aligned to available tools.
        """
        system_prompt = PLANNING_SYSTEM_PROMPT.format(tools=tool_descriptions)
        def _coerce_tasks(resp) -> List[Task]:
            import json
            if not resp:
                return []
            # Pydantic model
            if hasattr(resp, "tasks"):
                return [Task(**t.dict()) if hasattr(t, "dict") else Task(**t) for t in resp.tasks]  # type: ignore
            # Dict form
            if isinstance(resp, dict):
                tasks_field = resp.get("tasks")
                if isinstance(tasks_field, str):
                    try:
                        tasks_json = json.loads(tasks_field)
                        if isinstance(tasks_json, list):
                            return [Task(**_coerce_task_dict(i, idx+1)) for idx, i in enumerate(tasks_json)]
                    except Exception:
                        pass
                if isinstance(tasks_field, list):
                    return [Task(**_coerce_task_dict(i, idx+1)) for idx, i in enumerate(tasks_field)]
            # AIMessage/content JSON
            if hasattr(resp, "content") and isinstance(resp.content, str):  # type: ignore[attr-defined]
                try:
                    data = json.loads(resp.content)
                    if isinstance(data, dict) and isinstance(data.get("tasks"), list):
                        return [Task(**_coerce_task_dict(i, idx+1)) for idx, i in enumerate(data["tasks"])]
                except Exception:
                    pass
            # No luck
            return []

        def _coerce_task_dict(item, fallback_id: int) -> dict:
            if isinstance(item, dict):
                # Normalize common key variants
                desc = item.get("description") or item.get("desc") or item.get("task") or str(item)
                idv = item.get("id") or fallback_id
                done = item.get("done", False)
                return {"id": int(idv) if str(idv).isdigit() else fallback_id, "description": str(desc), "done": bool(done)}
            return {"id": fallback_id, "description": str(item), "done": False}

        try:
            response = call_llm(
                prompt, system_prompt=system_prompt, output_schema=TaskList
            )
            tasks = _coerce_tasks(response)
            if not tasks:
                raise ValueError("Empty or invalid task list from LLM")
        except Exception as e:
            this.logger._log(f"Planning failed: {e}")
            # Retry once with a clarified prompt to handle typos/ambiguous requests
            retry_prompt = f"""
            The user's request may contain typos or be ambiguous.
            First, rewrite it as a clear curriculum-development request with topic, audience, and level if implied.
            Then produce a JSON object with 3-6 atomic tasks aligned to available tools.

            Original request: "{query}"
            """
            try:
                response = call_llm(
                    retry_prompt, system_prompt=system_prompt, output_schema=TaskList
                )
                tasks = _coerce_tasks(response)
                if not tasks:
                    raise ValueError("Empty or invalid task list from retry")
            except Exception as e2:
                this.logger._log(f"Planning retry failed: {e2}")
                tasks = [Task(id=1, description=query, done=False)]

        task_dicts = [task.dict() for task in tasks]
        this.logger.log_task_list(task_dicts)
        return tasks

    # ---------- ask Model what to do ----------
    @show_progress("Thinking...", "")
    def plan_next_actions(this, task_desc: str, last_outputs: str = "") -> AIMessage:
        # last_outputs = textual feedback of what we just tried
        prompt = f"""
        We are working on: "{task_desc}".
        
        Last tool outputs: 
        ```
        {last_outputs}
        ```

        Given the task and the outputs, our next step is to:
        """
        try:
            return call_llm(prompt, system_prompt=ACTION_SYSTEM_PROMPT, tools=TOOLS)
        except Exception as e:
            this.logger._log(f"plan_next_actions failed: {e}")
            return AIMessage(content="Failed to get actions.")

    @show_progress("Checking if task is complete...", "")
    def ask_if_done(this, task_desc: str, recent_results: str) -> bool:
        prompt = f"""
        We are trying to complete task: "{task_desc}".
        Given the history of tool outputs so far: {recent_results}

        Is the task done?
        """
        try:
            resp = call_llm(
                prompt, system_prompt=VALIDATION_SYSTEM_PROMPT, output_schema=IsDone
            )
            return resp.done
        except:
            return False

    @show_progress("Checking if main goal is achieved...", "")
    def is_goal_achieved(this, query: str, task_outputs: list) -> bool:
        """Check if the overall goal is achieved based on all session outputs."""
        all_results = "\n\n".join(task_outputs)
        prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools so far:
        {all_results}
        
        Based on the data above, is the original query answered well?
        """
        try:
            resp = call_llm(
                prompt,
                system_prompt=META_VALIDATION_SYSTEM_PROMPT,
                output_schema=IsDone,
            )
            return resp.done
        except Exception as e:
            this.logger._log(f"Meta-validation failed: {e}")
            return False

    @show_progress("Optimizing tool call...", "")
    def optimize_tool_args(
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
        try:
            response = call_llm(
                prompt,
                system_prompt=get_tool_args_system_prompt(),
                output_schema=OptimizedToolArgs,
            )
            # Handle case where LLM returns dict directly instead of OptimizedToolArgs
            if response is None:
                return initial_args
            if isinstance(response, dict):
                return response if response else initial_args
            return response.arguments
        except Exception as e:
            this.logger._log(f"Argument optimization failed: {e}, using original args")
            return initial_args

    def _execute_tool(this, tool, tool_name: str, inp_args):
        """Execute a tool with progress indication."""

        # Create a dynamic decorator with the tool name
        @show_progress(f"Executing {tool_name}...", "")
        def run_tool():
            return tool.run(inp_args)

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
            if step_count >= this.max_steps:
                this.logger._log(
                    "Global max steps reached — aborting to avoid runaway loop."
                )
                break

            # Select the next incomplete task.
            task = next(task for task in tasks if not task.done)
            this.logger.log_task_start(task.description)

            # Define per-task state.
            per_task_steps = 0
            task_step_outputs = []  # outputs from a single step of a given task.

            # Loop through steps of a single task until the task is complete or the max steps are reached.
            while per_task_steps < this.max_steps_per_task:
                if step_count >= this.max_steps:
                    this.logger._log("Global max steps reached — stopping.")
                    return

                # Ask the LLM for the next action to take for the current task.
                ai_message = this.plan_next_actions(
                    task.description, last_outputs="\n".join(task_step_outputs)
                )

                # If no tool is called, the task is considered complete.
                if not ai_message.tool_calls:
                    task.done = True
                    this.logger.log_task_done(task.description)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    if step_count >= this.max_steps:
                        break

                    tool_name = tool_call["name"]
                    initial_args = tool_call["args"]

                    # Basic arg normalization: convert stringified lists to real lists
                    def _normalize_arg_value(v):
                        if isinstance(v, str) and v.startswith("[") and v.endswith("]"):
                            try:
                                import json, ast
                                try:
                                    parsed = json.loads(v)
                                except Exception:
                                    parsed = ast.literal_eval(v)
                                if isinstance(parsed, list):
                                    return parsed
                            except Exception:
                                return v
                        return v
                    initial_args = {k: _normalize_arg_value(v) for k, v in initial_args.items()}

                    # Refine tool arguments for better performance.
                    optimized_args = this.optimize_tool_args(
                        tool_name, initial_args, task.description
                    )

                    # Create a signature of the action to be taken.
                    action_sig = f"{tool_name}:{optimized_args}"

                    # Detect and prevent repetitive action loops.
                    last_actions.append(action_sig)
                    if len(last_actions) > 4:
                        last_actions = last_actions[-4:]
                    if len(set(last_actions)) == 1 and len(last_actions) == 4:
                        this.logger._log(
                            "Detected repeating action — aborting to avoid loop."
                        )
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
                                content=result
                            )
                            output = f"Output of {tool_name} with args {optimized_args}: {result}"
                            task_outputs.append(output)
                            task_step_outputs.append(output)
                        except Exception as e:
                            this.logger._log(f"Tool execution failed: {e}")
                            error_output = f"Error from {tool_name} with args {optimized_args}: {e}"
                            task_outputs.append(error_output)
                            task_step_outputs.append(error_output)
                    else:
                        this.logger._log(f"Invalid tool: {tool_name}")

                    step_count += 1
                    per_task_steps += 1

                # Task-level introspection: Check if the task is complete.
                if this.ask_if_done(task.description, "\n".join(task_step_outputs)):
                    task.done = True
                    this.logger.log_task_done(task.description)
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

    @show_progress("Generating answer...", "Answer ready")
    def _generate_answer(this, query: str, task_outputs: list) -> str:
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
        answer_obj = call_llm(
            answer_prompt,
            system_prompt=get_answer_system_prompt(),
            output_schema=Answer,
        )
        # Be robust to different return types
        try:
            if answer_obj is None:
                raise ValueError("Empty answer from LLM")
            if isinstance(answer_obj, dict):
                txt = answer_obj.get("answer")
                if not txt:
                    raise ValueError("Missing 'answer' in dict response")
                return txt
            # Pydantic model with .answer
            if hasattr(answer_obj, "answer"):
                return answer_obj.answer  # type: ignore[attr-defined]
            # Fallback to AIMessage-like content
            if hasattr(answer_obj, "content") and answer_obj.content:
                return str(answer_obj.content)
            # Last resort string conversion
            return str(answer_obj)
        except Exception:
            # Final fallback: return a synthesized summary from collected outputs
            fallback = [
                "Summary:",
                f"- Query: {query}",
                f"- Collected {len(task_outputs)} tool outputs.",
                "\nKey Outputs:",
            ]
            fallback.extend([f"- {o[:200]}" for o in task_outputs[-5:]])
            return "\n".join(fallback)
