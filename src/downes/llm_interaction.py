from typing import List, Dict
import re
from langchain_core.messages import AIMessage

from downes.model import call_llm
from downes.utils.ui import show_progress
from downes.prompts import (
    ACTION_SYSTEM_PROMPT,
    GET_ANSWER_SYSTEM_PROMPT,
    PLANNING_SYSTEM_PROMPT,
    GET_TOOL_ARGS_SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
    META_VALIDATION_SYSTEM_PROMPT,
)
from downes.task import Task
from downes.tools import TOOLS
from downes.utils.logger import Logger
from downes.utils.agent_helpers import (
    extract_content,
    is_affirmative,
    parse_markdown_checklist,
)

def call_llm_safe(
    prompt: str,
    system_prompt: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    tools=None,
    error_msg: str = "LLM call failed",
    operation_name: str = "LLM call",
):
    """Call LLM with error handling and logging."""
    if debug:
        logger._log(f"\n{'='*60}\n[DEBUG] {operation_name}")
        logger._log(f"[SYSTEM PROMPT]\n{system_prompt[:200]}...\n")
        logger._log(f"[USER PROMPT]\n{prompt[:500]}...\n")
    
    try:
        response = call_llm(
            prompt, 
            system_prompt=system_prompt, 
            tools=tools,
            verbose=verbose or debug
        )
        
        if debug and response:
            content = extract_content(response)
            logger._log(f"[RESPONSE]\n{content[:500]}...")
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger._log(f"[TOOL CALLS] {len(response.tool_calls)} call(s)")
            logger._log(f"{'='*60}\n")
        
        return response
    except Exception as e:
        logger._log(f"{error_msg}: {e}")
        return None

def plan_tasks_impl(query: str, logger: Logger, debug: bool, verbose: bool) -> List[Task]:
    @show_progress("Planning tasks...", "Tasks planned", enabled=not debug)
    def _impl():
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in TOOLS])
        prompt = f"""
        Given the user query: "{query}",
        Create a list of curriculum development tasks to be completed.
        Return tasks as a Markdown checklist.
        Keep tasks atomic and aligned to available tools.
        """
        system_prompt = PLANNING_SYSTEM_PROMPT.format(tools=tool_descriptions)

        response = call_llm_safe(
            prompt, system_prompt, logger, debug, verbose, error_msg="Planning failed", operation_name="Task Planning"
        )
        tasks = []
        if response:
            tasks = parse_markdown_checklist(extract_content(response))

        if not response or not tasks:
            # Retry once with a clarified prompt
            retry_prompt = f"""
            The user's request may contain typos or be ambiguous.
            First, rewrite it as a clear curriculum-development request with topic, audience, and level if implied.
            Then produce a Markdown checklist with 3-6 atomic tasks aligned to available tools.

            Original request: "{query}"
            """
            response = call_llm_safe(
                retry_prompt, system_prompt, logger, debug, verbose, error_msg="Planning retry failed", operation_name="Task Planning (Retry)"
            )
            tasks = (
                parse_markdown_checklist(extract_content(response))
                if response
                else []
            )

            if not tasks:
                tasks = [Task(id=1, description=query, done=False)]

        task_dicts = [task.dict() for task in tasks]
        logger.log_task_list(task_dicts)
        return tasks
    return _impl()

def plan_next_actions_impl(task_desc: str, logger: Logger, debug: bool, verbose: bool, last_outputs: str = "") -> AIMessage:
    @show_progress("Thinking...", "", enabled=not debug)
    def _impl():
        prompt = f"""
        We are working on: "{task_desc}".
        
        Last tool outputs: 
        ```
        {last_outputs}
        ```

        Given the task and the outputs, our next step is to:
        """
        response = call_llm_safe(
            prompt,
            ACTION_SYSTEM_PROMPT,
            logger,
            debug,
            verbose,
            tools=TOOLS,
            error_msg="plan_next_actions failed",
            operation_name="Action Planning",
        )
        return response if response else AIMessage(content="Failed to get actions.")
    return _impl()

def ask_if_done_impl(task_desc: str, recent_results: str, logger: Logger, debug: bool, verbose: bool) -> bool:
    @show_progress("Checking if task is complete...", "", enabled=not debug)
    def _impl():
        prompt = f"""
        We are trying to complete task: "{task_desc}".
        Given the history of tool outputs so far: {recent_results}

        Is the task done?
        """
        response = call_llm_safe(
            prompt, VALIDATION_SYSTEM_PROMPT, logger, debug, verbose, error_msg="Task validation failed", operation_name="Task Validation"
        )
        return (
            is_affirmative(extract_content(response)) if response else False
        )
    return _impl()

def is_goal_achieved_impl(query: str, task_outputs: list, logger: Logger, debug: bool, verbose: bool) -> bool:
    """Check if the overall goal is achieved based on all session outputs."""
    @show_progress("Checking if main goal is achieved...", "", enabled=not debug)
    def _impl():
        all_results = "\n\n".join(task_outputs)
        prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools so far:
        {all_results}
        
        Based on the data above, is the original query answered well?
        """
        response = call_llm_safe(
            prompt, META_VALIDATION_SYSTEM_PROMPT, logger, debug, verbose, error_msg="Meta-validation failed", operation_name="Goal Validation"
        )
        return (
            is_affirmative(extract_content(response)) if response else False
        )
    return _impl()

def optimize_tool_args_impl(
    tool_name: str, initial_args: dict, task_desc: str, logger: Logger, debug: bool, verbose: bool
) -> dict:
    """Optimize tool arguments based on task requirements."""
    @show_progress("Optimizing tool call...", "", enabled=not debug)
    def _impl():
        tool = next((t for t in TOOLS if t.name == tool_name), None)
        if not tool:
            return initial_args

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
        response = call_llm_safe(
            prompt,
            GET_TOOL_ARGS_SYSTEM_PROMPT(),
            logger,
            debug,
            verbose,
            error_msg="Argument optimization failed",
            operation_name="Argument Optimization",
        )
        if response:
            content = extract_content(response)

            optimized = {}
            code_block_match = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1)

            for line in content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    try:
                        import ast
                        optimized[key] = ast.literal_eval(value)
                    except:
                        optimized[key] = value

            return {**initial_args, **optimized} if optimized else initial_args
        else:
            return initial_args
    return _impl()

def generate_answer_impl(query: str, task_outputs: list, logger: Logger, debug: bool, verbose: bool) -> str:
    """Generate the final answer based on collected data."""
    @show_progress("Generating answer...", "Answer ready", enabled=not debug)
    def _impl():
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
        response = call_llm_safe(
            answer_prompt,
            GET_ANSWER_SYSTEM_PROMPT(),
            logger,
            debug,
            verbose,
            error_msg="Answer generation failed, using fallback",
            operation_name="Answer Generation",
        )
        if response:
            content = extract_content(response)
            if content:
                return content

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
    return _impl()
