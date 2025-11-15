import sys
import time
import threading
from contextlib import contextmanager
from typing import Optional, Callable
from functools import wraps


class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    WHITE = "\033[97m"
    LIGHT_BLUE = "\033[94m"  # Same as   ASCII art


class Spinner:
    """An animated spinner that runs in a separate thread."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(this, message: str = "", color: str = Colors.CYAN):
        this.message = message
        this.color = color
        this.running = False
        this.thread: Optional[threading.Thread] = None

    def _animate(this):
        """Animation loop that runs in a separate thread."""
        idx = 0
        while this.running:
            frame = this.FRAMES[idx % len(this.FRAMES)]
            sys.stdout.write(f"\r{this.color}{frame}{Colors.ENDC} {this.message}")
            sys.stdout.flush()
            time.sleep(0.08)
            idx += 1

    def start(this):
        """Start the spinner animation."""
        if not this.running:
            this.running = True
            this.thread = threading.Thread(target=this._animate, daemon=True)
            this.thread.start()

    def stop(
        this,
        final_message: str = "",
        symbol: str = "✓",
        symbol_color: str = Colors.GREEN,
    ):
        """Stop the spinner and optionally show a completion message."""
        if this.running:
            this.running = False
            if this.thread:
                this.thread.join()
            # Clear the line
            sys.stdout.write("\r" + " " * (len(this.message) + 10) + "\r")
            if final_message:
                print(f"{symbol_color}{symbol}{Colors.ENDC} {final_message}")
            sys.stdout.flush()

    def update_message(this, message: str):
        """Update the spinner message."""
        this.message = message


def show_progress(message: str, success_message: str = "", enabled: bool = True):
    """Decorator to show progress spinner while a function executes.
    
    Args:
        message: The message to display while running
        success_message: Optional message to display on success
        enabled: Whether to actually show the spinner (for debug/verbose modes)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled:
                # Skip spinner entirely in debug mode
                return func(*args, **kwargs)
            
            spinner = Spinner(message, color=Colors.CYAN)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                spinner.stop(
                    success_message or message.replace("...", " ✓"),
                    symbol="✓",
                    symbol_color=Colors.GREEN,
                )
                return result
            except Exception as e:
                spinner.stop(f"Failed: {str(e)}", symbol="✗", symbol_color=Colors.RED)
                raise

        return wrapper

    return decorator


class UI:
    """Interactive UI for displaying agent progress and results."""

    def __init__(this):
        this.current_spinner: Optional[Spinner] = None

    @contextmanager
    def progress(this, message: str, success_message: str = ""):
        """Context manager for showing progress with a spinner."""
        spinner = Spinner(message, color=Colors.CYAN)
        this.current_spinner = spinner
        spinner.start()
        try:
            yield spinner
            spinner.stop(
                success_message or message.replace("...", " ✓"),
                symbol="✓",
                symbol_color=Colors.GREEN,
            )
        except Exception as e:
            spinner.stop(f"Failed: {str(e)}", symbol="✗", symbol_color=Colors.RED)
            raise
        finally:
            this.current_spinner = None

    def print_header(this, text: str):
        """Print a section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}╭─ {text}{Colors.ENDC}")

    def print_user_query(this, query: str):
        """Print the user's query in the same style as   ASCII art."""
        print(f"\n{Colors.BOLD}{Colors.LIGHT_BLUE}You: {query}{Colors.ENDC}\n")

    def print_step_list(this, steps):
        """Print a clean list of planned steps."""
        if not steps:
            return
        this.print_header("Planned Steps")
        for i, step in enumerate(steps):
            status = "+"
            color = Colors.DIM
            desc = step.get("description", step)
            print(f"{Colors.BLUE}│{Colors.ENDC} {color}{status}{Colors.ENDC} {desc}")
        print(f"{Colors.BLUE}╰{'─' * 50}{Colors.ENDC}\n")

    def print_step_start(this, step_desc: str):
        """Print when starting a step."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}▶ Step:{Colors.ENDC} {step_desc}")

    def print_step_done(this, step_desc: str):
        """Print when a step is completed."""
        print(
            f"{Colors.GREEN}  ✓ Completed{Colors.ENDC} {Colors.DIM}│ {step_desc}{Colors.ENDC}"
        )

    def print_tool_params(this, params: str):
        """Print tool parameters before execution."""
        params_display = (
            f" {Colors.DIM}{params}{Colors.ENDC}" if params and len(params) > 0 else ""
        )
        print(f"  {Colors.MAGENTA}→{Colors.ENDC}  Parameters: {params_display}")

    def print_tool_run(this, result: str):
        """Print when a tool is executed."""
        result_display = (
            f" {Colors.DIM}({result[:150]}...){Colors.ENDC}"
            if result and len(result) > 0
            else ""
        )
        print(f"  {Colors.YELLOW}⚡{Colors.ENDC} Result: {result_display}")

    def print_answer(this, answer: str):
        """Print the final answer in a beautiful box."""
        width = 80

        # Top border
        print(f"\n{Colors.BOLD}{Colors.BLUE}╔{'═' * (width - 2)}╗{Colors.ENDC}")

        # Title
        title = "ANSWER"
        padding = (width - len(title) - 2) // 2
        print(
            f"{Colors.BOLD}{Colors.BLUE}║{' ' * padding}{title}{' ' * (width - len(title) - padding - 2)}║{Colors.ENDC}"
        )

        # Separator
        print(f"{Colors.BLUE}╠{'═' * (width - 2)}╣{Colors.ENDC}")

        # Answer content with proper line wrapping
        print(
            f"{Colors.BLUE}║{Colors.ENDC}{' ' * (width - 2)}{Colors.BLUE}║{Colors.ENDC}"
        )
        for line in answer.split("\n"):
            if len(line) == 0:
                print(
                    f"{Colors.BLUE}║{Colors.ENDC}{' ' * (width - 2)}{Colors.BLUE}║{Colors.ENDC}"
                )
            else:
                # Word wrap long lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= width - 6:
                        current_line += word + " "
                    else:
                        if current_line:
                            print(
                                f"{Colors.BLUE}║{Colors.ENDC} {current_line.ljust(width - 4)} {Colors.BLUE}║{Colors.ENDC}"
                            )
                        current_line = word + " "
                if current_line:
                    print(
                        f"{Colors.BLUE}║{Colors.ENDC} {current_line.ljust(width - 4)} {Colors.BLUE}║{Colors.ENDC}"
                    )

        print(
            f"{Colors.BLUE}║{Colors.ENDC}{' ' * (width - 2)}{Colors.BLUE}║{Colors.ENDC}"
        )

        # Bottom border
        print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * (width - 2)}╝{Colors.ENDC}\n")

    def print_info(this, message: str):
        """Print an info message."""
        print(f"{Colors.DIM}{message}{Colors.ENDC}")

    def print_error(this, message: str):
        """Print an error message."""
        print(f"{Colors.RED}✗ Error:{Colors.ENDC} {message}")

    def print_warning(this, message: str):
        """Print a warning message."""
        print(f"{Colors.YELLOW}⚠ Warning:{Colors.ENDC} {message}")

    def prompt_for_input(this, prompt_text: str, default: str = "") -> str:
        """Prompt user for input with optional default value."""
        if default:
            prompt_text = f"{prompt_text} [{default}]: "
        else:
            prompt_text = f"{prompt_text}: "
        
        try:
            response = input(f"{Colors.CYAN}{prompt_text}{Colors.ENDC}").strip()
            return response if response else default
        except (EOFError, KeyboardInterrupt):
            print()
            return default

    def confirm(this, question: str, default: bool = True) -> bool:
        """Ask a yes/no question and return boolean response."""
        default_str = "Y/n" if default else "y/N"
        response = this.prompt_for_input(f"{question} ({default_str})", "y" if default else "n")
        return response.lower() in ["y", "yes", "true", "1"] if response else default

    def print_prompt_preview(this, system_prompt: str, user_prompt: str, operation_name: str):
        """Display prompt preview in debug mode."""
        width = 80
        
        # Header
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'─' * width}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}📝 PROMPT PREVIEW: {operation_name}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'─' * width}{Colors.ENDC}\n")
        
        # System Prompt
        print(f"{Colors.BOLD}{Colors.YELLOW}[SYSTEM PROMPT]{Colors.ENDC}")
        print(f"{Colors.DIM}{system_prompt}{Colors.ENDC}\n")
        
        # User Prompt
        print(f"{Colors.BOLD}{Colors.CYAN}[USER PROMPT]{Colors.ENDC}")
        print(f"{user_prompt}\n")
        
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'─' * width}{Colors.ENDC}\n")
