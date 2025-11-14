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
	1. Dedents the text to remove the common leading whitespace
	2. Re-indents all lines to match the substitution position
	3. Preserves the internal formatting (like bullet points, nested indentation)
	
	Args:
		text: The multi-line text to process
		indent: Number of spaces to indent continuation lines
		indent_first: If True, also indent the first line (default: False)
	
	Returns:
		Properly indented text for f-string substitution with formatting preserved
		
	Example:
		>>> description = "Line 1\\n  - Bullet\\n  - Another"
		>>> f"Tool: {indent_multiline(description, 6)}"
		'Tool: Line 1\\n        - Bullet\\n        - Another'
	"""
	if not text:
		return text
	
	# First dedent to remove common leading whitespace
	dedented = textwrap.dedent(text)
	
	# Split into lines
	lines = dedented.splitlines()
	
	if len(lines) <= 1:
		return dedented.strip()
	
	# Prepare indentation string
	indent_str = ' ' * indent
	
	# Build result, preserving internal formatting
	result = []
	for i, line in enumerate(lines):
		if i == 0:
			# First line - optionally indent, preserve any internal spacing
			if indent_first:
				result.append(indent_str + line if line else '')
			else:
				result.append(line)
		else:
			# Subsequent lines - indent but preserve internal formatting
			if line:
				result.append(indent_str + line)
			else:
				result.append('')  # Preserve empty lines
	
	# Strip trailing whitespace from the whole result
	return '\n'.join(result).rstrip()


__all__ = ["no", "strip_or_empty", "indent_multiline"]
