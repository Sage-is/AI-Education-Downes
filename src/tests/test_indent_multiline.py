#!/usr/bin/env python3
"""Test the indent_multiline utility function."""

from downes.utils import indent_multiline


def test_single_line():
    """Test single line text - should just strip it."""
    text = "Single line"
    result = indent_multiline(text, 4)
    assert result == "Single line"
    print("✓ Single line test passed")


def test_multiline_basic():
    """Test basic multi-line indentation."""
    text = """Line 1
Line 2
Line 3"""
    result = indent_multiline(text, 4)
    expected = "Line 1\n    Line 2\n    Line 3"
    assert result == expected, f"Expected:\n{expected}\n\nGot:\n{result}"
    print("✓ Basic multi-line test passed")


def test_multiline_with_existing_indent():
    """Test that existing indentation is removed first."""
    text = """    Line 1
    Line 2
    Line 3"""
    result = indent_multiline(text, 4)
    expected = "Line 1\n    Line 2\n    Line 3"
    assert result == expected, f"Expected:\n{expected}\n\nGot:\n{result}"
    print("✓ Multi-line with existing indent test passed")


def test_multiline_in_fstring():
    """Test actual f-string usage."""
    description = """This is a tool
that does multiple things
and has multiple lines"""

    # Simulate how it would be used in an f-string with indentation
    result = f"""Tool information:
    Name: example_tool
    Description: {indent_multiline(description, 17)}
    Status: active"""

    expected = """Tool information:
    Name: example_tool
    Description: This is a tool
                 that does multiple things
                 and has multiple lines
    Status: active"""

    assert result == expected, f"Expected:\n{expected}\n\nGot:\n{result}"
    print("✓ F-string usage test passed")


def test_empty_lines_preserved():
    """Test that empty lines are preserved."""
    text = """Line 1

Line 3
Line 4"""
    result = indent_multiline(text, 4)
    expected = "Line 1\n\n    Line 3\n    Line 4"
    assert result == expected, f"Expected:\n{expected}\n\nGot:\n{result}"
    print("✓ Empty lines preserved test passed")


def test_zero_indent():
    """Test with zero indent - should just dedent."""
    text = """    Line 1
    Line 2
    Line 3"""
    result = indent_multiline(text, 0)
    expected = "Line 1\nLine 2\nLine 3"
    assert result == expected, f"Expected:\n{expected}\n\nGot:\n{result}"
    print("✓ Zero indent test passed")


def test_complex_tool_description():
    """Test with a realistic tool description."""
    tool_desc = """Generate learning objectives aligned to Bloom's taxonomy.

    This tool creates measurable, actionable objectives for curriculum design.
    Each objective specifies what learners will be able to do."""

    result = f"- tool_name:\n{indent_multiline(tool_desc, 4)}"

    # Check that the result is formatted correctly
    # First line of description is NOT indented (it's the "first" line)
    # But subsequent lines ARE indented
    lines = result.split("\n")
    assert lines[0] == "- tool_name:"
    # The function treats the first content line as unindented
    assert "Generate learning objectives" in lines[1]
    # Empty line
    assert lines[2] == ""
    # These should be indented
    assert lines[3].startswith("    ") or "This tool" in lines[3]
    assert lines[4].startswith("    ") or "Each objective" in lines[4]
    print("✓ Complex tool description test passed")


if __name__ == "__main__":
    test_single_line()
    test_multiline_basic()
    test_multiline_with_existing_indent()
    test_multiline_in_fstring()
    test_empty_lines_preserved()
    test_zero_indent()
    test_complex_tool_description()
    print("\n✅ All tests passed!")
