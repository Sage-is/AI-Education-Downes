from typing import List, Dict, Optional
import ast
import re
from langchain_core.messages import AIMessage

from downes.model import call_llm
from downes.utils import no, indent_multiline, format_for_template
from downes.utils.ui import show_progress, Colors
from downes.prompts import (
    ACTION_SYSTEM_PROMPT,
    GET_ANSWER_SYSTEM_PROMPT,
    PLANNING_SYSTEM_PROMPT,
    GET_TOOL_ARGS_SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
    META_VALIDATION_SYSTEM_PROMPT,
)
from downes.steps import Step
from downes.tools import TOOLS, get_tool
from downes.utils.logger import Logger
from downes.utils.vault import Vault
from downes.utils.agent_helpers import (
    extract_content,
    is_affirmative,
    parse_markdown_checklist,
    normalize_arg_value,
)
import tempfile
import subprocess
import os


def _edit_text_in_editor(text: str, title: str = "Edit") -> str:
    """Open text in system editor for editing."""
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tf:
        tf.write(f"# {title}\n# Save and close this file when done editing\n\n")
        tf.write(text)
        tf.flush()
        temp_path = tf.name

    try:
        subprocess.run([editor, temp_path], check=True)

        with open(temp_path, "r") as f:
            lines = f.readlines()
            # Remove comment lines at the top
            content_lines = [line for line in lines if not line.strip().startswith("#")]
            return "".join(content_lines).strip()
    finally:
        os.unlink(temp_path)


def _review_and_edit_prompt(
    prompt: str,
    system_prompt: str,
    operation_name: str,
    logger: Logger,
) -> tuple[str, str]:
    """Allow user to review and optionally edit prompts before submission."""

    # Display the prompt preview
    logger.ui.print_prompt_preview(system_prompt, prompt, operation_name)

    # Interactive menu
    while True:
        print(f"{Colors.BOLD}Options:{Colors.ENDC}")
        print(f"  {Colors.GREEN}[s]{Colors.ENDC} Submit as-is")
        print(f"  {Colors.YELLOW}[e]{Colors.ENDC} Edit user prompt")
        print(f"  {Colors.YELLOW}[E]{Colors.ENDC} Edit system prompt")
        print(f"  {Colors.CYAN}[v]{Colors.ENDC} View full prompts")
        print(f"  {Colors.RED}[c]{Colors.ENDC} Cancel (skip this LLM call)\n")

        choice = logger.ui.prompt_for_input("Your choice", "s").lower()

        if choice == "s" or choice == "":
            print(f"{Colors.GREEN}✓ Submitting prompt...{Colors.ENDC}\n")
            return prompt, system_prompt

        elif choice == "e":
            print(f"{Colors.YELLOW}Opening editor for user prompt...{Colors.ENDC}")
            try:
                edited_prompt = _edit_text_in_editor(prompt, "Edit User Prompt")
                if edited_prompt:
                    prompt = edited_prompt
                    print(f"{Colors.GREEN}✓ User prompt updated{Colors.ENDC}\n")
                    logger.ui.print_prompt_preview(
                        system_prompt, prompt, operation_name
                    )
                else:
                    print(f"{Colors.YELLOW}⚠ No changes made{Colors.ENDC}\n")
            except Exception as e:
                print(f"{Colors.RED}✗ Error editing: {e}{Colors.ENDC}\n")

        elif choice == "E":
            print(f"{Colors.YELLOW}Opening editor for system prompt...{Colors.ENDC}")
            try:
                edited_system = _edit_text_in_editor(
                    system_prompt, "Edit System Prompt"
                )
                if edited_system:
                    system_prompt = edited_system
                    print(f"{Colors.GREEN}✓ System prompt updated{Colors.ENDC}\n")
                    logger.ui.print_prompt_preview(
                        system_prompt, prompt, operation_name
                    )
                else:
                    print(f"{Colors.YELLOW}⚠ No changes made{Colors.ENDC}\n")
            except Exception as e:
                print(f"{Colors.RED}✗ Error editing: {e}{Colors.ENDC}\n")

        elif choice == "v":
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
            print(f"{Colors.BOLD}FULL SYSTEM PROMPT:{Colors.ENDC}\n")
            print(f"{system_prompt}\n")
            print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
            print(f"{Colors.BOLD}FULL USER PROMPT:{Colors.ENDC}\n")
            print(f"{prompt}\n")
            print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}\n")

        elif choice == "c":
            if logger.ui.confirm(
                "Are you sure you want to cancel this LLM call?", default=False
            ):
                print(f"{Colors.RED}✗ LLM call cancelled{Colors.ENDC}\n")
                return None, None
            else:
                print()

        else:
            print(f"{Colors.RED}Invalid choice. Please try again.{Colors.ENDC}\n")


def call_llm_safe(
    prompt: str,
    system_prompt: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    tools=None,
    error_msg: str = "LLM call failed",
    operation_name: str = "LLM call",
    vault: Optional[Vault] = None,
):
    """Call LLM with error handling and logging."""

    # Interactive prompt review in debug mode
    if debug:
        prompt, system_prompt = _review_and_edit_prompt(
            prompt, system_prompt, operation_name, logger
        )

        # User cancelled
        if prompt is None or system_prompt is None:
            logger._log(f"[DEBUG] {operation_name} - CANCELLED BY USER")
            return None

        logger._log(f"\n{'='*60}\n[DEBUG] {operation_name} - SUBMITTING")

    should_record = vault is not None and (debug or verbose)
    metadata = {
        "operation": operation_name,
        "tools_bound": [getattr(t, "name", "unknown") for t in (tools or [])],
        "verbose": verbose,
        "debug": debug,
    }

    try:
        response = call_llm(
            prompt, system_prompt=system_prompt, tools=tools, verbose=verbose or debug
        )

        if debug and response:
            content = extract_content(response)
            # logger._log(f"[RESPONSE]\n{content[:500]}...")
            logger._log(f"[RESPONSE]\n{content}...")
            if hasattr(response, "tool_calls") and response.tool_calls:
                logger._log(f"[TOOL CALLS] {len(response.tool_calls)} call(s)")
            logger._log(f"{'='*60}\n")

        if response and hasattr(response, "response_metadata"):
            metadata["response_metadata"] = response.response_metadata

        if should_record:
            vault.save_llm_transcript(
                operation_name=operation_name,
                prompt=prompt,
                system_prompt=system_prompt,
                response=response,
                metadata=metadata,
            )

        return response
    except Exception as e:
        logger._log(f"{error_msg}: {e}")
        if should_record:
            error_metadata = {**metadata, "error": str(e)}
            vault.save_llm_transcript(
                operation_name=f"{operation_name} (error)",
                prompt=prompt,
                system_prompt=system_prompt,
                response=str(e),
                metadata=error_metadata,
            )
        return None


def plan_steps_impl(
    query: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    vault: Optional[Vault] = None,
) -> List[Step]:
    @show_progress("Planning steps...", "Steps planned", enabled=not debug)
    def _impl():
        tool_descriptions = "\n\n".join(
            [f"- {t.name}:\n  {indent_multiline(t.description, 2)}" for t in TOOLS]
        )
        prompt = f"""
        Project: "{query}",

        **Note:** Only return the atomic steps as a markdown checklist. Each step should be a clear, actionable step that can be completed using the available tools.
        """
        # Use format_for_template to auto-detect indentation
        system_prompt = format_for_template(
            PLANNING_SYSTEM_PROMPT, tools=tool_descriptions
        )

        response = call_llm_safe(
            prompt,
            system_prompt,
            logger,
            debug,
            verbose,
            error_msg="Planning failed",
            operation_name="Step Planning",
            vault=vault,
        )
        steps = []
        if response:
            steps = parse_markdown_checklist(extract_content(response))

        if no(response) or no(steps):
            # Retry once with a clarified prompt
            retry_prompt = f"""
            The request may contain typos or be ambiguous.
            Rewrite it as a clear curriculum-development request with topic, audience, and level (if implied).

            Then produce a Markdown checklist with 3-6 atomic steps aligned to available tools.

            ```
                - [ ] step 1
                - [ ] step 2
                - [ ] step 3
            ```
            
            Original request: "{query}"
            """
            response = call_llm_safe(
                retry_prompt,
                system_prompt,
                logger,
                debug,
                verbose,
                error_msg="Planning retry failed",
                operation_name="Step Planning (Retry)",
                vault=vault,
            )
            steps = (
                parse_markdown_checklist(extract_content(response)) if response else []
            )

            if not steps:
                steps = [Step(id=1, description=query, done=False)]

        step_dicts = [step.dict() for step in steps]
        logger.log_step_list(step_dicts)
        return steps

    return _impl()


def plan_next_actions_impl(
    step_desc: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    last_outputs: str = "",
    vault: Optional[Vault] = None,
) -> AIMessage:
    @show_progress("Thinking...", "", enabled=not debug)
    def _impl():
        prompt = f"""
        We are working on: "{step_desc}".
        
        Last tool outputs: 
        ```
        {indent_multiline(last_outputs, 8)}
        ```

        Given the step and the outputs, our next step is to:
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
            vault=vault,
        )
        return response if response else AIMessage(content="Failed to get actions.")

    return _impl()


def ask_if_done_impl(
    step_desc: str,
    recent_results: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    vault: Optional[Vault] = None,
) -> bool:
    @show_progress("Checking if step is complete...", "", enabled=not debug)
    def _impl():
        prompt = f"""
        We are trying to complete step: "{step_desc}".
        
        Given the history of tool outputs so far:
        {indent_multiline(recent_results, 4)}

        Is the step done?
        """
        response = call_llm_safe(
            prompt,
            VALIDATION_SYSTEM_PROMPT,
            logger,
            debug,
            verbose,
            error_msg="Step validation failed",
            operation_name="Step Validation",
            vault=vault,
        )
        return is_affirmative(extract_content(response)) if response else False

    return _impl()


def is_goal_achieved_impl(
    query: str,
    step_outputs: list,
    logger: Logger,
    debug: bool,
    verbose: bool,
    vault: Optional[Vault] = None,
) -> bool:
    """Check if the overall goal is achieved based on all session outputs."""

    @show_progress("Checking if main goal is achieved...", "", enabled=not debug)
    def _impl():
        all_results = "\n\n".join(step_outputs)
        prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools so far:
        {indent_multiline(all_results, 8)}
        
        Based on the data above, is the original query answered well?
        """
        response = call_llm_safe(
            prompt,
            META_VALIDATION_SYSTEM_PROMPT,
            logger,
            debug,
            verbose,
            error_msg="Meta-validation failed",
            operation_name="Goal Validation",
            vault=vault,
        )
        return is_affirmative(extract_content(response)) if response else False

    return _impl()


def optimize_tool_args_impl(
    tool_name: str,
    initial_args: dict,
    step_desc: str,
    logger: Logger,
    debug: bool,
    verbose: bool,
    vault: Optional[Vault] = None,
) -> dict:
    """Optimize tool arguments based on step requirements."""

    @show_progress("Optimizing tool call...", "", enabled=not debug)
    def _impl():
        tool = get_tool(tool_name)
        if not tool:
            return initial_args

        tool_description = tool.description
        tool_schema = (
            tool.args_schema.schema()
            if hasattr(tool, "args_schema") and tool.args_schema
            else {}
        )

        prompt = f"""
        Step: "{step_desc}"
        Tool: {tool_name}
        Tool Description:
        {indent_multiline(tool_description, 8)}
        Tool Parameters:
        {indent_multiline(str(tool_schema), 8)}
        Initial Arguments:
        {indent_multiline(str(initial_args), 8)}
        
        Given the step, optimize the arguments to ensure all relevant parameters are used correctly.
        *Note:Pay special attention to filtering parameters that would help narrow down results to match the step.*
        """
        response = call_llm_safe(
            prompt,
            GET_TOOL_ARGS_SYSTEM_PROMPT(),
            logger,
            debug,
            verbose,
            error_msg="Argument optimization failed",
            operation_name="Argument Optimization",
            vault=vault,
        )
        if response:
            content = extract_content(response)

            def _strip_inline_comment(raw: str) -> str:
                if not isinstance(raw, str):
                    return raw
                cleaned = raw.strip().rstrip(",")
                if not cleaned:
                    return cleaned
                # Remove trailing sentences wrapped in parentheticals (LLM explanations)
                if (
                    " (" in cleaned
                    and cleaned.endswith(")")
                    and not cleaned.startswith(("'", '"'))
                ):
                    cleaned = cleaned[: cleaned.rfind(" (")].strip().rstrip(".")
                return cleaned

            def _parse_scalar(raw: str):
                if raw is None:
                    return None
                if not isinstance(raw, str):
                    return raw
                cleaned = _strip_inline_comment(raw)
                if not cleaned:
                    return ""
                lowered = cleaned.lower()
                if lowered in {"true", "false"}:
                    return lowered == "true"
                if lowered in {"null", "none"}:
                    return None
                # Try numeric conversion
                try:
                    if lowered.startswith("0x"):
                        return int(lowered, 16)
                    return int(cleaned)
                except ValueError:
                    try:
                        return float(cleaned)
                    except ValueError:
                        pass
                # Try to interpret JSON/Python literals
                if cleaned.startswith(("[", "{", "(", "'", '"')) and cleaned[-1] in (
                    "]",
                    "}",
                    ")",
                    "'",
                    '"',
                ):
                    try:
                        return ast.literal_eval(cleaned)
                    except Exception:
                        pass
                return cleaned

            def _parse_structured_args(text: str) -> dict:
                optimized_args: dict = {}
                current_key: Optional[str] = None

                for raw_line in text.splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower().startswith("argument_name"):
                        continue

                    if line.startswith("-") and current_key:
                        item = line[1:].strip()
                        parsed_item = _parse_scalar(item)
                        optimized_args.setdefault(current_key, [])
                        optimized_args[current_key].append(parsed_item)
                        continue

                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if not key:
                            continue
                        if not value:
                            optimized_args[key] = []
                            current_key = key
                            continue

                        parsed_value = _parse_scalar(value)
                        optimized_args[key] = parsed_value
                        current_key = key if isinstance(parsed_value, list) else None
                        continue

                    current_key = None

                return optimized_args

            code_block_match = re.search(r"```[^\n]*\n(.*?)\n```", content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1)

            optimized = _parse_structured_args(content)

            if not optimized:
                return initial_args

            merged_args = dict(initial_args)
            for key, value in optimized.items():
                if isinstance(value, list):
                    merged_args[key] = [normalize_arg_value(item) for item in value]
                else:
                    merged_args[key] = normalize_arg_value(value)

            return merged_args
        else:
            return initial_args

    return _impl()


def generate_answer_impl(
    query: str,
    step_outputs: list,
    logger: Logger,
    debug: bool,
    verbose: bool,
    vault: Optional[Vault] = None,
) -> str:
    """Generate the final answer based on collected data."""

    @show_progress("Generating answer...", "Answer ready", enabled=not debug)
    def _impl():
        all_results = (
            "\n\n".join(step_outputs) if step_outputs else "No data was collected."
        )
        answer_prompt = f"""
        Original user query: "{query}"
        
        Data and results collected from tools:
        {indent_multiline(all_results, 8)}
        
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
            vault=vault,
        )
        if response:
            content = extract_content(response)
            if content:
                return content

        fallback = [
            "# Summary",
            "",
            f"**Query:** {query}",
            f"**Outputs Collected:** {len(step_outputs)}",
            "",
            "## Key Outputs",
            "",
        ]
        fallback.extend([f"- {o[:200]}..." for o in step_outputs[-5:]])
        return "\n".join(fallback)

    return _impl()
