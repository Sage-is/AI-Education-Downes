from downes.steps import Step
from downes.tools import invoke_tool
from downes.utils.logger import Logger
from downes.utils.ui import show_progress


def mark_step_done(step: Step, logger: Logger):
    """Mark a step as complete and log it."""
    step.done = True
    logger.log_step_done(step.description)


def check_step_limit(
    step_count: int, max_steps: int, logger: Logger, context: str = "Global"
) -> bool:
    """Check if step limit is reached and log if so."""
    if step_count >= max_steps:
        logger._log(f"{context} max steps reached — aborting to avoid runaway loop.")
        return True
    return False


def detect_loop(last_actions: list, action_sig: str, logger: Logger) -> bool:
    """Detect if we're stuck in a repeating action loop."""
    last_actions.append(action_sig)
    if len(last_actions) > 4:
        last_actions[:] = last_actions[-4:]  # Modify in place

    if len(set(last_actions)) == 1 and len(last_actions) == 4:
        logger._log("Detected repeating action — aborting to avoid loop.")
        return True
    return False


def execute_tool(tool, tool_name: str, inp_args, logger: Logger, debug: bool):
    """Execute a tool with progress indication."""

    @show_progress(f"Executing {tool_name}...", "", enabled=not debug)
    def run_tool():
        if debug:
            logger._log(f"[TOOL EXECUTION] {tool_name} with args: {inp_args}")
        result = invoke_tool(tool, inp_args)
        if debug:
            result_preview = str(result)[:200] if result else "None"
            logger._log(f"[TOOL RESULT] {result_preview}...")
        return result

    return run_tool()


def confirm_action(tool: str, input_str: str) -> bool:
    """
    Confirm whether to execute a given action.

    In a production environment, this would prompt the user for confirmation.
    For this example, we log and auto-confirm. Risky tools are not
    implemented in this version.
    """
    # TODO logging
    # logging.info(f"CONFIRMING ACTION: Tool={tool}, Input='{input_str}'")
    return True
