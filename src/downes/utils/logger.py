from downes.utils.ui import UI
from typing import Optional


class Logger:
    """Logger that uses the new interactive UI system."""

    def __init__(this, verbose: bool = False, ui: Optional[UI] = None):
        this.ui = ui if ui else UI()
        this.log = []
        this.verbose = verbose

    def _log(this, msg: str):
        """Print immediately and keep in log."""
        print(msg, flush=True)
        this.log.append(msg)

    def log_header(this, msg: str):
        this.ui.print_header(msg)

    def log_user_query(this, query: str):
        this.ui.print_user_query(query)

    def log_step_list(this, steps):
        this.ui.print_step_list(steps)

    def log_step_start(this, step_desc: str):
        this.ui.print_step_start(step_desc)

    def log_step_done(this, step_desc: str):
        this.ui.print_step_done(step_desc)

    def log_tool_run(this, params: dict, result: dict):
        this.ui.print_tool_params(str(params))
        this.ui.print_tool_run(str(result))

    def log_risky(this, tool: str, input_str: str):
        this.ui.print_warning(f"Risky action {tool}({input_str}) — auto-confirmed")

    def log_summary(this, summary: str):
        this.ui.print_answer(summary)

    def progress(this, message: str, success_message: str = ""):
        """Return a progress context manager for showing loading states."""
        return this.ui.progress(message, success_message)
