"""Generic utilities shared across the project."""

import textwrap
from typing import Any


def no(value: Any) -> bool:
	"""Return the logical negation of ``value`` for readability helpers."""
	return not value


def strip_or_empty(value: Any) -> str:
	"""Return ``value`` stripped as text, or ``""`` when missing."""
	if value is None:
		return ""
	return str(value).strip()


def indent_multiline(text: str, indent: int = 0, indent_first: bool = False) -> str:
	"""Dedent and re-indent multi-line text to match f-string substitution position.
	
	This function solves the problem where multi-line variables inserted into f-strings
	don't inherit the horizontal indentation. It:
	1. Dedents the text to remove existing indentation
	2. Re-indents lines to match the substitution position
	
	Args:
		text: The multi-line text to process
		indent: Number of spaces to indent continuation lines
		indent_first: If True, also indent the first line (default: False)
	
	Returns:
		Properly indented text for f-string substitution
		
	Example:
		>>> description = "Line 1\\nLine 2\\nLine 3"
		>>> f"Tool: {indent_multiline(description, 6)}"
		'Tool: Line 1\\n      Line 2\\n      Line 3'
	"""
	if not text:
		return text
	
	# First dedent to remove existing indentation
	dedented = textwrap.dedent(text)
	
	# Split into lines
	lines = dedented.splitlines()
	
	if len(lines) <= 1:
		return dedented.strip()
	
	# Prepare indentation string
	indent_str = ' ' * indent
	
	# Build result
	result = []
	for i, line in enumerate(lines):
		if i == 0:
			# First line - optionally indent
			if indent_first:
				result.append(indent_str + line.strip() if line.strip() else '')
			else:
				result.append(line.strip())
		else:
			# Subsequent lines - always indent non-empty lines
			if line.strip():
				result.append(indent_str + line.strip())
			else:
				result.append('')  # Preserve empty lines
	
	return '\n'.join(result)


__all__ = ["no", "strip_or_empty", "indent_multiline"]
