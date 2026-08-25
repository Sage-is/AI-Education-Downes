#!/usr/bin/env python3
"""Demonstration of the indent_multiline fix for f-string formatting issues."""

from src.downes.utils import indent_multiline


def show_problem():
    """Show the original problem with multi-line f-string substitution."""
    print("=" * 80)
    print("PROBLEM: Multi-line variable in f-string without indent_multiline")
    print("=" * 80)

    tool_desc = """Generate learning objectives aligned to Bloom's taxonomy.

This tool creates measurable, actionable objectives for curriculum design.
Each objective specifies what learners will be able to do."""

    # Without indent_multiline - lines don't align
    bad_result = f"""Available Tools:
    - generate_objectives:
        {tool_desc}
    - draft_syllabus:
        Create a comprehensive syllabus"""

    print(bad_result)
    print("\nNotice how 'This tool creates...' is not aligned with the tool description!")
    print()


def show_solution():
    """Show how indent_multiline fixes the problem."""
    print("=" * 80)
    print("SOLUTION: Using indent_multiline to properly format")
    print("=" * 80)

    tool_desc = """Generate learning objectives aligned to Bloom's taxonomy.

This tool creates measurable, actionable objectives for curriculum design.
Each objective specifies what learners will be able to do."""

    # With indent_multiline - lines align properly
    good_result = f"""Available Tools:
    - generate_objectives:
        {indent_multiline(tool_desc, 8)}
    - draft_syllabus:
        Create a comprehensive syllabus"""

    print(good_result)
    print("\nNow all lines are properly aligned!")
    print()


def show_inline_usage():
    """Show inline usage where first line should NOT be indented."""
    print("=" * 80)
    print("INLINE USAGE: Variable on same line as other text")
    print("=" * 80)

    description = """A multi-line description
that continues on the next line
and the line after that."""

    # When inline, first line shouldn't be indented
    result = f"Tool: {indent_multiline(description, 6)}"

    print(result)
    print("\nFirst line is inline, subsequent lines are indented to match!")
    print()


def show_newline_usage():
    """Show usage where variable starts on a new line."""
    print("=" * 80)
    print("NEWLINE USAGE: Variable starts on new line (with indent_first=True)")
    print("=" * 80)

    description = """A multi-line description
that continues on the next line
and the line after that."""

    # When on new line, all lines should be indented
    result = f"""Tool Information:
    Name: example_tool
    Description:
        {indent_multiline(description, 8, indent_first=True)}
    Status: active"""

    print(result)
    print("\nAll lines including the first are indented!")
    print()


if __name__ == "__main__":
    show_problem()
    show_solution()
    show_inline_usage()
    show_newline_usage()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
The indent_multiline() utility solves the f-string multi-line formatting problem by:

1. Dedenting the input text (removes existing indentation)
2. Re-indenting subsequent lines to match the position in the f-string
3. Supporting optional first-line indentation for newline contexts

Usage:
    indent_multiline(text, indent_spaces, indent_first=False)

Parameters:
    - text: The multi-line string to format
    - indent_spaces: Number of spaces to indent continuation lines
    - indent_first: Whether to also indent the first line (default: False)

This ensures proper Markdown and text formatting in LLM prompts!
    """)
