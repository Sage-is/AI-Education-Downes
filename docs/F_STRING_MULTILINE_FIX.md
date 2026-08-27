# F-String Multi-line Formatting Fix

## Problem Statement

When inserting multi-line variables into Python f-strings with triple quotes, only the first line appears at the correct horizontal position. Subsequent lines start at the beginning of the line instead of inheriting the indentation of the variable's position in the f-string. This causes formatting issues, especially with Markdown in LLM prompts.

### Example of the Problem

```python
description = """First line
Second line
Third line"""

# Without fix:
result = f"""
Tool: {description}
"""

# Output (broken):
# Tool: First line
# Second line
# Third line
```

The second and third lines don't align with "First line" - they start at column 0 instead of being indented to match.

## Solution: `indent_multiline()` Utility

The `indent_multiline()` function in `src/downes/utils/__init__.py` solves this by:

1. **Dedenting** the input text using `textwrap.dedent()` to remove existing indentation
2. **Re-indenting** subsequent lines to match the substitution position in the f-string
3. **Preserving** empty lines while only indenting lines with content

### Function Signature

```python
def indent_multiline(
    text: str,
    indent: int = 0,
    indent_first: bool = False
) -> str:
    """Dedent and re-indent multi-line text to match f-string substitution position."""
```

### Parameters

- **`text`**: The multi-line string to process
- **`indent`**: Number of spaces to indent continuation lines
- **`indent_first`**: If `True`, also indent the first line (default: `False`)

### Usage Examples

#### Example 1: Inline Substitution

When the variable appears inline with other text on the same line:

```python
from downes.utils import indent_multiline

description = """First line
Second line
Third line"""

result = f"Tool: {indent_multiline(description, 6)}"
# Output:
# Tool: First line
#       Second line
#       Third line
```

The first line stays inline, subsequent lines indent to column 6 to align.

#### Example 2: Block Substitution

When building structured prompts with nested indentation:

```python
tool_desc = """Generate learning objectives aligned to Bloom's taxonomy.

This tool creates measurable, actionable objectives for curriculum design.
Each objective specifies what learners will be able to do."""

prompt = f"""Available Tools:
    - generate_objectives:
        {indent_multiline(tool_desc, 8)}
    - draft_syllabus:
        Create a comprehensive syllabus"""

# Output:
# Available Tools:
#     - generate_objectives:
#         Generate learning objectives aligned to Bloom's taxonomy.
#
#         This tool creates measurable, actionable objectives for curriculum design.
#         Each objective specifies what learners will be able to do.
#     - draft_syllabus:
#         Create a comprehensive syllabus
```

#### Example 3: First Line Indentation

When you want ALL lines (including the first) to be indented:

```python
description = """A multi-line description
that continues on the next line
and the line after that."""

result = f"""Tool Information:
    Description:
        {indent_multiline(description, 8, indent_first=True)}"""

# Output:
# Tool Information:
#     Description:
#         A multi-line description
#         that continues on the next line
#         and the line after that.
```

## Implementation in `llm_interaction.py`

The fix has been applied to all f-string prompts in `llm_interaction.py`:

### 1. Tool Descriptions in Planning

```python
tool_descriptions = "\n\n".join([
    f"- {t.name}:\n{indent_multiline(t.description, 4)}"
    for t in TOOLS
])
system_prompt = PLANNING_SYSTEM_PROMPT.format(
    tools=indent_multiline(tool_descriptions, 0)
)
```

### 2. Last Outputs in Action Planning

```python
prompt = f"""
We are working on: "{task_desc}".

Last tool outputs:

\`\`\`
{indent_multiline(last_outputs, 8)}
\`\`\`

"""
```

### 3. Recent Results in Task Validation

```python
prompt = f"""
We are trying to complete task: "{task_desc}".
Given the history of tool outputs so far:
{indent_multiline(recent_results, 8)}

Is the task done?
"""
```

### 4. All Results in Goal Validation

```python
prompt = f"""
Original user query: "{query}"

Data and results collected from tools so far:
{indent_multiline(all_results, 8)}

Based on the data above, is the original query answered well?
"""
```

### 5. Tool Arguments Optimization

```python
prompt = f"""
Task: "{task_desc}"
Tool: {tool_name}
Tool Description:
{indent_multiline(tool_description, 8)}
Tool Parameters:
{indent_multiline(str(tool_schema), 8)}
Initial Arguments:
{indent_multiline(str(initial_args), 8)}
"""
```

### 6. Answer Generation

```python
answer_prompt = f"""
Original user query: "{query}"

Data and results collected from tools:
{indent_multiline(all_results, 8)}

Based on the data above, provide a comprehensive answer to the user's query.
"""
```

## Benefits

1. **Proper Markdown Formatting**: LLM prompts maintain correct Markdown structure
2. **Readable Code**: Clear indentation makes prompts easier to understand
3. **Consistent Formatting**: All multi-line insertions follow the same pattern
4. **No Manual Formatting**: Automatic handling eliminates error-prone manual indentation

## Testing

Run the test suite to verify the fix:

```bash
# Test the utility function
python src/tests/test_indent_multiline.py

# View demonstration
python demo_indent_fix.py

# Run existing tests to ensure compatibility
uv run python src/tests/test_education_tools.py
```

## Technical Notes

- The function uses `textwrap.dedent()` to normalize input first
- Empty lines are preserved but not indented
- Single-line strings are returned as-is (just stripped)
- The `indent_first` parameter handles both inline and block contexts
- All text is stripped of leading/trailing whitespace per line

## Future Considerations

This utility can be reused anywhere multi-line text needs to be inserted into formatted strings:

- Configuration file generation
- Code generation
- Documentation generation
- Any structured text output
