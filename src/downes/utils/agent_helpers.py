from typing import List
import re
import json
import ast

from downes.steps import Step


def extract_content(response) -> str:
    """Extract text content from LLM response."""
    return response.content if hasattr(response, "content") else str(response)


def is_affirmative(text: str) -> bool:
    """Check if text starts with yes/affirmative response."""
    return text.strip().lower().startswith("yes")


def normalize_arg_value(value):
    """
    Convert stringified JSON values to Python types.
    
    LLMs often pass JSON-serialized values as strings (e.g., 'null', '[1,2,3]')
    instead of proper Python types. This method normalizes them to prevent
    Pydantic validation errors.
    
    Handles:
    - 'null'/'none' → None (for Optional fields)
    - '[...]' → list (for List fields)
    - Malformed JSON → empty list (for safety)
    """
    if isinstance(value, str):
        stripped = value.strip()
        
        # Handle JSON null
        if stripped.lower() in ('null', 'none', ''):
            return None
        
        # Handle JSON lists (including malformed ones)
        if stripped.startswith("["):
            # Check for malformed/incomplete JSON
            if not stripped.endswith("]") or len(stripped) <= 2:
                return []  # Return empty list for malformed JSON
            
            try:
                try:
                    parsed = json.loads(stripped)
                except Exception:
                    parsed = ast.literal_eval(stripped)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return []  # Return empty list if parsing fails
    
    return value


def format_output(
    tool_name: str, args: dict, result_or_error, is_error: bool = False
) -> str:
    """Format tool execution output or error message."""
    prefix = "Error from" if is_error else "Output of"
    return f"{prefix} {tool_name} with args {args}: {result_or_error}"


def parse_markdown_checklist(text: str) -> List[Step]:
    """Parse a Markdown checklist into Step objects"""
    steps = []
    # Match checklist items: - [ ] Step description
    pattern = r"-\s*\[\s*\]\s*(.+?)(?=\n-\s*\[|$)"
    matches = re.findall(pattern, text, re.DOTALL)

    for idx, match in enumerate(matches, start=1):
        description = match.strip()
        if description and not description.startswith("(none"):
            steps.append(Step(id=idx, description=description, done=False))

    return steps
