from downes.tools import get_tool
from downes.utils.logger import Logger
from downes.utils.vault import Vault
from typing import Optional
from downes.utils.agent_helpers import (
    normalize_arg_value,
    format_output,
    bind_llm_call,
    guard_step_limit,
    finalize_run,
)
from downes.utils import no
from downes.llm_interaction import (
    plan_steps_impl,
    plan_next_actions_impl,
    generate_answer_impl,
)
from downes.utils.execution_helpers import (
    mark_step_done,
    detect_loop,
    execute_tool,
    confirm_action,
)


class Agent:
    def __init__(
        this,
        max_steps: int = 20,
        max_steps_per_step: int = 5,
        verbose: bool = False,
        debug: bool = False,
        logger: Logger = None,
    ):
        this.logger = logger if logger else Logger(verbose=verbose)
        this.max_steps = max_steps  # global safety cap
        this.max_steps_per_step = max_steps_per_step
        this.vault = Vault()
        this.verbose = verbose
        this.debug = debug

        class LLM: pass

        this.llm = LLM()
        this.llm.plan_steps = bind_llm_call(
            plan_steps_impl, 
            this.logger, 
            this.debug, 
            this.verbose, 
            this.vault
        )
        this.llm.plan_next_actions = bind_llm_call(
            plan_next_actions_impl,
            this.logger,
            this.debug,
            this.verbose,
            this.vault,
        )
        this.llm.generate_answer = bind_llm_call(
            generate_answer_impl, 
            this.logger, 
            this.debug, 
            this.verbose, 
            this.vault
        )

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
        steps = this.llm.plan_steps(query)

        # If no steps were created, the query is likely out of scope.
        if no(steps):
            return finalize_run(
                this.llm.generate_answer, query, step_outputs, this.logger, this.vault
            )

        # 2. Loop through steps sequentially.
        for the_step in steps:
            this.logger.log_step_start(the_step.description)

            # Define per-step state.
            per_step_steps = 0
            step_step_outputs = []  # outputs from a single step of a given step.

            # Loop through steps of a single step until the step is complete or the max steps are reached.
            while per_step_steps < this.max_steps_per_step:
                limit_hit, safety_stop_reason = guard_step_limit(
                    step_count, this.max_steps, this.logger, safety_stop_reason
                )
                if limit_hit:
                    safety_stop = True
                    break

                # Ask the LLM for the next action to take for the current step.
                ai_message = this.llm.plan_next_actions(
                    the_step.description, last_outputs="\n".join(step_step_outputs)
                )

                # If no tool is called, the step is considered complete.
                if not ai_message.tool_calls:
                    mark_step_done(the_step, this.logger)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    limit_hit, safety_stop_reason = guard_step_limit(
                        step_count, this.max_steps, this.logger, safety_stop_reason
                    )
                    if limit_hit:
                        safety_stop = True
                        break

                    tool_name = tool_call["name"]
                    initial_args = tool_call["args"]

                    # Basic arg normalization: convert stringified lists to real lists
                    optimized_args = {
                        k: normalize_arg_value(v) for k, v in initial_args.items()
                    }

                    # Detect and prevent repetitive action loops.
                    action_sig = f"{tool_name}:{optimized_args}"
                    if detect_loop(last_actions, action_sig, this.logger):
                        # Instead of stopping, warn the LLM to encourage replanning/adjusting
                        warning = f"SYSTEM WARNING: You are repeating the action {tool_name} with args {optimized_args}. This is a loop. You MUST change your approach or arguments."
                        step_step_outputs.append(warning)
                        step_count += 1
                        per_step_steps += 1
                        continue

                    # Execute the tool.
                    tool_to_run = get_tool(tool_name)
                    if tool_to_run and confirm_action(tool_name, str(optimized_args)):
                        try:
                            result = execute_tool(
                                tool_to_run,
                                tool_name,
                                optimized_args,
                                this.logger,
                                this.debug,
                            )
                            this.logger.log_tool_run(optimized_args, result)
                            this.vault.save_artifact(
                                step_name=the_step.description,
                                artifact_name=tool_name,
                                content=result,
                            )
                            output = format_output(tool_name, optimized_args, result)
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

                if safety_stop:
                    break

                # Step-level introspection removed to save tokens.
                # We rely on plan_next_actions to return no tool calls when done.
                # if this.llm.ask_if_done(
                #     the_step.description, "\n".join(step_step_outputs)
                # ):
                #     mark_step_done(the_step, this.logger)
                #     break

            # Global introspection removed. We trust the plan and execute all steps.
            # if the_step.done and this.llm.is_goal_achieved(query, step_outputs):
            #     this.logger._log("Main goal achieved. Finalizing answer.")
            #     break

            if safety_stop:
                break

        reason = safety_stop_reason if safety_stop else None
        return finalize_run(
            this.llm.generate_answer,
            query,
            step_outputs,
            this.logger,
            this.vault,
            reason=reason,
        )
