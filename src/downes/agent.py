from typing import List

from langchain_core.messages import AIMessage

from downes.steps import Step
from downes.tools import TOOLS, get_tool
from downes.utils.logger import Logger
from downes.utils.vault import Vault
from downes.utils.agent_helpers import (
    normalize_arg_value,
    format_output,
)
from downes.utils import no
from downes.llm_interaction import (
    plan_steps_impl,
    plan_next_actions_impl,
    ask_if_done_impl,
    is_goal_achieved_impl,
    optimize_tool_args_impl,
    generate_answer_impl,
)
from downes.utils.execution_helpers import (
    mark_step_done,
    check_step_limit,
    detect_loop,
    execute_tool,
    confirm_action,
)


class Agent:
    def __init__(this, max_steps: int = 20, max_steps_per_step: int = 5, verbose: bool = False, debug: bool = False):
        this.logger = Logger(verbose=verbose)
        this.max_steps = max_steps  # global safety cap
        this.max_steps_per_step = max_steps_per_step
        this.vault = Vault()
        this.verbose = verbose
        this.debug = debug

    # ---------- step planning ----------
    def plan_steps(this, query: str) -> List[Step]:
        """Plan steps for the given query."""
        return plan_steps_impl(query, this.logger, this.debug, this.verbose, this.vault)

    # ---------- ask Model what to do ----------
    def plan_next_actions(this, step_desc: str, last_outputs: str = "") -> AIMessage:
        """Plan next actions."""
        return plan_next_actions_impl(step_desc, this.logger, this.debug, this.verbose, last_outputs, this.vault)

    def ask_if_done(this, step_desc: str, recent_results: str) -> bool:
        """Check if step is done."""
        return ask_if_done_impl(step_desc, recent_results, this.logger, this.debug, this.verbose, this.vault)

    def is_goal_achieved(this, query: str, step_outputs: list) -> bool:
        """Check if goal is achieved."""
        return is_goal_achieved_impl(query, step_outputs, this.logger, this.debug, this.verbose, this.vault)

    def optimize_tool_args(
        this, tool_name: str, initial_args: dict, step_desc: str
    ) -> dict:
        """Optimize tool arguments."""
        return optimize_tool_args_impl(tool_name, initial_args, step_desc, this.logger, this.debug, this.verbose, this.vault)

    def run(this, query: str):
        """
        Executes the main agent loop to process a user query.

        This method orchestrates the entire process of understanding a query,
        planning steps, executing tools to gather information, and synthesizing
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
        step_outputs = []  # outputs from all steps
        safety_stop = False
        safety_stop_reason = None

        # 1. Decompose the user query into a list of steps.
        steps = this.plan_steps(query)

        # If no steps were created, the query is likely out of scope.
        if no(steps):
            answer = this._generate_answer(query, step_outputs)
            this.logger.log_summary(answer)
            return answer

        # 2. Loop through steps until all steps are complete or the max steps are reached.
        while any(not the_step.done for the_step in steps):
            # Global safety break.
            if check_step_limit(step_count, this.max_steps, this.logger, "Global"):
                safety_stop = True
                safety_stop_reason = safety_stop_reason or "Global max steps reached — pausing for human assistance."
                answer = this._generate_answer(query, step_outputs)
                this.logger.log_summary(answer)
                return answer

            # Select the next incomplete step.
            the_step = next(the_step for the_step in steps if not the_step.done)
            this.logger.log_step_start(the_step.description)

            # Define per-step state.
            per_step_steps = 0
            step_step_outputs = []  # outputs from a single step of a given step.

            # Loop through steps of a single step until the step is complete or the max steps are reached.
            while per_step_steps < this.max_steps_per_step:
                if check_step_limit(step_count, this.max_steps, this.logger, "Global"):
                    safety_stop = True
                    safety_stop_reason = safety_stop_reason or "Global max steps reached — pausing for human assistance."
                    break

                # Ask the LLM for the next action to take for the current step.
                ai_message = this.plan_next_actions(
                    the_step.description, last_outputs="\n".join(step_step_outputs)
                )

                # If no tool is called, the step is considered complete.
                if not ai_message.tool_calls:
                    mark_step_done(the_step, this.logger)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    if step_count >= this.max_steps:
                        safety_stop = True
                        safety_stop_reason = safety_stop_reason or "Global max steps reached — pausing for human assistance."
                        break

                    tool_name = tool_call["name"]
                    initial_args = tool_call["args"]

                    # Basic arg normalization: convert stringified lists to real lists
                    initial_args = {
                        k: normalize_arg_value(v) for k, v in initial_args.items()
                    }

                    # Refine tool arguments for better performance.
                    optimized_args = this.optimize_tool_args(
                        tool_name, initial_args, the_step.description
                    )

                    # Detect and prevent repetitive action loops.
                    action_sig = f"{tool_name}:{optimized_args}"
                    if detect_loop(last_actions, action_sig, this.logger):
                        safety_stop = True
                        safety_stop_reason = safety_stop_reason or "Potential action loop detected — pausing for human assistance."
                        break

                    # Execute the tool.
                    tool_to_run = get_tool(tool_name)
                    if tool_to_run and confirm_action(
                        tool_name, str(optimized_args)
                    ):
                        try:
                            result = execute_tool(
                                tool_to_run, tool_name, optimized_args, this.logger, this.debug
                            )
                            this.logger.log_tool_run(optimized_args, result)
                            this.vault.save_artifact(
                                step_name=the_step.description,
                                artifact_name=tool_name,
                                content=result,
                            )
                            output = format_output(
                                tool_name, optimized_args, result
                            )
                            step_outputs.append(output)
                            step_step_outputs.append(output)
                        except Exception as e:
                            this.logger._log(f"Tool execution failed: {e}")
                            error_output = format_output(
                                tool_name, optimized_args, e, is_error=True
                            )
                            step_outputs.append(error_output)
                            step_step_outputs.append(error_output)
                    else:
                        this.logger._log(f"Invalid tool: {tool_name}")

                    step_count += 1
                    per_step_steps += 1

                    if step_count >= this.max_steps:
                        safety_stop = True
                        safety_stop_reason = safety_stop_reason or "Global max steps reached — pausing for human assistance."
                        break

                if safety_stop:
                    break

                # Step-level introspection: Check if the step is complete.
                if this.ask_if_done(the_step.description, "\n".join(step_step_outputs)):
                    mark_step_done(the_step, this.logger)
                    break

            # Global introspection: Check if the overall goal is achieved.
            if the_step.done and this.is_goal_achieved(query, step_outputs):
                this.logger._log("Main goal achieved. Finalizing answer.")
                break

            if safety_stop:
                break

        # Generate the final answer from all collected tool outputs.
        if safety_stop:
            human_help_note = safety_stop_reason or "Global max steps reached — pausing for human assistance."
            this.logger._log(human_help_note)
            step_outputs.append(human_help_note)

        answer = this._generate_answer(query, step_outputs)
        this.logger.log_summary(answer)
        this.vault.save_artifact("summary", "final_answer", answer)
        return answer

    def _generate_answer(this, query: str, step_outputs: list) -> str:
        """Generate answer."""
        return generate_answer_impl(query, step_outputs, this.logger, this.debug, this.verbose, this.vault)
