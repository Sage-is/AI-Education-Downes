from downes.utils.ui import UI


class Logger:
    """Logger that uses the new interactive UI system."""

    def __init__(this):
        this.ui = UI()
        this.log = []

    def _log(this, msg: str):
        """Print immediately and keep in log."""
        print(msg, flush=True)
        this.log.append(msg)

    def log_header(this, msg: str):
        this.ui.print_header(msg)

    def log_user_query(this, query: str):
        this.ui.print_user_query(query)

    def log_task_list(this, tasks):
        this.ui.print_task_list(tasks)

    def log_task_start(this, task_desc: str):
        this.ui.print_task_start(task_desc)

    def log_task_done(this, task_desc: str):
        this.ui.print_task_done(task_desc)

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
