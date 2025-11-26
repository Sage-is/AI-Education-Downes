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
        this.max_steps = max_steps  
        this.max_steps_per_step = max_steps_per_step
        this.vault = Vault()
        this.verbose = verbose
        this.debug = debug

        class LLM: pass

        this.llm = LLM()
        this.llm.plan_steps = bind_llm_call(plan_steps_impl, this)
        this.llm.plan_next_actions = bind_llm_call(plan_next_actions_impl, this)
        this.llm.generate_answer = bind_llm_call(generate_answer_impl, this)

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
        total_steps = 0
        last_actions = []
        run_history = []  # outputs from all steps
        safety_stop = False
        safety_stop_reason = None

        # 1. Decompose the user query into a list of steps.
        steps = this.llm.plan_steps(query)

        # If no steps were created, the query is likely out of scope.
        if no(steps):
            return finalize_run(this, query, run_history)

        # 2. Loop through steps sequentially.
        for current_step in steps:
            this.logger.log_step_start(current_step.description)

            # Define per-step state.
            action_count = 0
            step_history = []  # outputs from a single step of a given step.

            # Loop through steps of a single step until the step is complete or the max steps are reached.
            while action_count < this.max_steps_per_step:
                limit_hit, safety_stop_reason = guard_step_limit(
                    this, total_steps, safety_stop_reason
                )
                if limit_hit:
                    safety_stop = True
                    break

                # Ask the LLM for the next action to take for the current step.
                ai_message = this.llm.plan_next_actions(
                    current_step.description, last_outputs="\n".join(step_history)
                )

                # If no tool is called, the step is considered complete.
                if not ai_message.tool_calls:
                    mark_step_done(current_step, this.logger)
                    break

                # Process each tool call returned by the LLM.
                for tool_call in ai_message.tool_calls:
                    limit_hit, safety_stop_reason = guard_step_limit(
                        this, total_steps, safety_stop_reason
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
                        # Instead of stopping, warn the LLM and encourage replanning/adjusting
                        warning = f"""
                            SYSTEM WARNING: You are repeating the action {tool_name} with args {optimized_args}. 
                            This is a loop. You MUST change your approach or arguments."""
                        step_history.append(warning)
                        total_steps += 1
                        action_count += 1
                        continue

                    # Execute the tool.
                    tool_to_run = get_tool(tool_name)
                    if tool_is_ready(tool_to_run) and user_confirms(tool_name, optimized_args):
                        try:
                            result = run_the_tool(tool_to_run, tool_name, optimized_args, this)
                            log_the_result(this, optimized_args, result)
                            save_the_artifact(this, current_step, tool_name, result)
                            
                            output = format_output(tool_name, optimized_args, result)
                            record_the_outcome(run_history, step_history, output)
                        except Exception as error:
                            handle_tool_error(this, tool_name, optimized_args, error, run_history, step_history)
                    else:
                        log_invalid_tool(this, tool_name)

                    total_steps += 1
                    action_count += 1

                if safety_stop:
                    break

            if safety_stop:
                break

        reason = safety_stop_reason if safety_stop else None
        return finalize_run(this, query, run_history, reason=reason)

# --- HyperTalk-style Helper Functions ---

def tool_is_ready(tool):
    return tool is not None

def user_confirms(tool_name, args):
    return confirm_action(tool_name, str(args))

def run_the_tool(tool, name, args, agent):
    return execute_tool(
        tool,
        name,
        args,
        agent.logger,
        agent.debug,
    )

def log_the_result(agent, args, result):
    agent.logger.log_tool_run(args, result)

def save_the_artifact(agent, step, name, result):
    agent.vault.save_artifact(
        step_name=step.description,
        artifact_name=name,
        content=result,
    )

def record_the_outcome(run_history, step_history, output):
    run_history.append(output)
    step_history.append(output)

def handle_tool_error(agent, tool_name, args, error, run_history, step_history):
    agent.logger._log(f"Tool execution failed: {error}")
    error_output = format_output(
        tool_name, args, error, is_error=True
    )
    run_history.append(error_output)
    step_history.append(error_output)

def log_invalid_tool(agent, tool_name):
    agent.logger._log(f"Invalid tool: {tool_name}")
