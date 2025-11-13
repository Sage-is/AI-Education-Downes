from typing import List

from langchain_core.messages import AIMessage

from downes.task import Task
from downes.tools import TOOLS
from downes.utils.logger import Logger
from downes.utils.vault import Vault
from downes.utils.agent_helpers import (
    normalize_arg_value,
    format_output,
)
from downes.llm_interaction import (
    plan_tasks_impl,
    plan_next_actions_impl,
    ask_if_done_impl,
    is_goal_achieved_impl,
    optimize_tool_args_impl,
    generate_answer_impl,
)
from downes.utils.execution_helpers import (
    mark_task_done,
    check_step_limit,
    detect_loop,
    execute_tool,
    confirm_action,
)


class Agent:
    def __init__(this, max_steps: int = 20, max_steps_per_task: int = 5, verbose: bool = False, debug: bool = False):
        this.logger = Logger(verbose=verbose)
        this.max_steps = max_steps  # global safety cap
        this.max_steps_per_task = max_steps_per_task
        this.vault = Vault()
        this.verbose = verbose
        this.debug = debug

    # ---------- task planning ----------
    def plan_tasks(this, query: str) -> List[Task]:
        """Plan tasks for the given query."""
        return plan_tasks_impl(query, this.logger, this.debug, this.verbose, this.vault)

    # ---------- ask Model what to do ----------
    def plan_next_actions(this, task_desc: str, last_outputs: str = "") -> AIMessage:
        """Plan next actions."""
        return plan_next_actions_impl(task_desc, this.logger, this.debug, this.verbose, last_outputs, this.vault)

    def ask_if_done(this, task_desc: str, recent_results: str) -> bool:
        """Check if task is done."""
        return ask_if_done_impl(task_desc, recent_results, this.logger, this.debug, this.verbose, this.vault)

    def is_goal_achieved(this, query: str, task_outputs: list) -> bool:
        """Check if goal is achieved."""
        return is_goal_achieved_impl(query, task_outputs, this.logger, this.debug, this.verbose, this.vault)

    def optimize_tool_args(
        this, tool_name: str, initial_args: dict, task_desc: str
    ) -> dict:
        """Optimize tool arguments."""
        return optimize_tool_args_impl(tool_name, initial_args, task_desc, this.logger, this.debug, this.verbose, this.vault)

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
            if check_step_limit(step_count, this.max_steps, this.logger, "Global"):
                break

            # Select the next incomplete task.
            task = next(task for task in tasks if not task.done)
            this.logger.log_task_start(task.description)

            # Define per-task state.
            per_task_steps = 0
            task_step_outputs = []  # outputs from a single step of a given task.

            # Loop through steps of a single task until the task is complete or the max steps are reached.
            while per_task_steps < this.max_steps_per_task:
                if check_step_limit(step_count, this.max_steps, this.logger, "Global"):
                    return

                # Ask the LLM for the next action to take for the current task.
                ai_message = this.plan_next_actions(
                    task.description, last_outputs="\n".join(task_step_outputs)
                )

                # If no tool is called, the task is considered complete.
                if not ai_message.tool_calls:
                    mark_task_done(task, this.logger)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    if step_count >= this.max_steps:
                        break

                    tool_name = tool_call["name"]
                    initial_args = tool_call["args"]

                    # Basic arg normalization: convert stringified lists to real lists
                    initial_args = {
                        k: normalize_arg_value(v) for k, v in initial_args.items()
                    }

                    # Refine tool arguments for better performance.
                    optimized_args = this.optimize_tool_args(
                        tool_name, initial_args, task.description
                    )

                    # Detect and prevent repetitive action loops.
                    action_sig = f"{tool_name}:{optimized_args}"
                    if detect_loop(last_actions, action_sig, this.logger):
                        return

                    # Execute the tool.
                    tool_to_run = next((t for t in TOOLS if t.name == tool_name), None)
                    if tool_to_run and confirm_action(
                        tool_name, str(optimized_args)
                    ):
                        try:
                            result = execute_tool(
                                tool_to_run, tool_name, optimized_args, this.logger, this.debug
                            )
                            this.logger.log_tool_run(optimized_args, result)
                            this.vault.save_artifact(
                                task_name=task.description,
                                artifact_name=tool_name,
                                content=result,
                            )
                            output = format_output(
                                tool_name, optimized_args, result
                            )
                            task_outputs.append(output)
                            task_step_outputs.append(output)
                        except Exception as e:
                            this.logger._log(f"Tool execution failed: {e}")
                            error_output = format_output(
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
                    mark_task_done(task, this.logger)
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
        """Generate answer."""
        return generate_answer_impl(query, task_outputs, this.logger, this.debug, this.verbose, this.vault)
