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


def format_for_template(template: str, **kwargs) -> str:
	"""Format a template string while auto-detecting indentation for multi-line values.
	
	This function improves upon str.format() by:
	1. Detecting the indentation level of each placeholder in the template
	2. Automatically applying indent_multiline() to multi-line values
	3. Preserving the internal formatting of the values
	
	Args:
		template: The template string with {placeholder} markers
		**kwargs: Key-value pairs to substitute into the template
	
	Returns:
		Formatted string with proper indentation for all multi-line values
		
	Example:
		>>> template = '''
		... Tools:
		...     {tools}
		... Done.
		... '''
		>>> tools = "- tool1:\\n  Description"
		>>> format_for_template(template, tools=tools)
		# tools will be indented by 4 spaces to match its position
	"""
	import re
	
	# Process each value that's multi-line
	formatted_kwargs = {}
	
	for key, value in kwargs.items():
		# Only process string values with newlines
		if not isinstance(value, str) or '\n' not in value:
			formatted_kwargs[key] = value
			continue
		
		# Find the placeholder and its indentation context
		pattern = rf'^(\s*)(.*)?\{{{key}\}}'
		indent_detected = False
		
		for line in template.split('\n'):
			match = re.match(pattern, line)
			if match:
				line_indent = len(match.group(1))
				before_placeholder = match.group(2) or ''
				
				# Calculate the position where the placeholder's content starts
				if not before_placeholder.strip():
					# Placeholder is at the start of the line (after whitespace)
					# Apply the line's indentation to all lines
					formatted_kwargs[key] = indent_multiline(value, line_indent)
				else:
					# Placeholder is inline after some content
					# Calculate the column position for continuation lines
					placeholder_column = len(match.group(1)) + len(before_placeholder)
					formatted_kwargs[key] = indent_multiline(value, placeholder_column)
				
				indent_detected = True
				break
		
		if not indent_detected:
			# Couldn't find the placeholder, use value as-is
			formatted_kwargs[key] = value
	
	# Now do the normal format
	return template.format(**formatted_kwargs)


__all__ = ["no", "strip_or_empty", "indent_multiline", "format_for_template"]
