# Auto-Detecting Indentation for Multi-line String Formatting

## Overview

When working with f-strings and template strings in Python, multi-line variable substitutions create formatting challenges. The first line appears at the correct horizontal position, but subsequent lines don't inherit that indentation, causing misaligned output especially problematic for Markdown-formatted LLM prompts.

We've solved this with two utility functions that automatically handle indentation:

- **`indent_multiline()`** - Dedents and re-indents text while preserving internal structure
- **`format_for_template()`** - Auto-detects placeholder indentation and applies it automatically

## The Problem

### Before: Broken Formatting

```python
description = """First line of description
Second line of description
Third line of description"""

prompt = f"""
Available tools:
    {description}
Done.
"""

# Output (broken):
# Available tools:
#     First line of description
# Second line of description
# Third line of description
# Done.
```

The second and third lines start at column 0 instead of aligning at column 4.

## The Solution

### Using `format_for_template()` (Recommended)

```python
from downes.utils import format_for_template

template = """
Available tools:
    {description}
Done.
"""

description = """First line of description
Second line of description
Third line of description"""

result = format_for_template(template, description=description)

# Output (correct):
# Available tools:
#     First line of description
#     Second line of description
#     Third line of description
# Done.
```

**The function automatically detects that `{description}` has 4 spaces of indentation and applies it to all continuation lines!**

### Using `indent_multiline()` (Manual Control)

```python
from downes.utils import indent_multiline

description = """First line
Second line
Third line"""

# Manually specify indentation
formatted = indent_multiline(description, indent=4)

prompt = f"""
Tools:
    {formatted}
Done.
"""
```

## Key Features

### 1. Auto-Detection of Indentation

`format_for_template()` analyzes the template string to determine where each placeholder appears:

- **Block placeholders** - At the start of a line (after whitespace)
  ```python
  template = """
  Section:
      {content}
  """
  # Auto-detects: indent=4
  ```

- **Inline placeholders** - After other content on the same line
  ```python
  template = "Tool: {description}"
  # Auto-detects: indent=6 (to align after "Tool: ")
  ```

### 2. Preservation of Internal Formatting

Both functions preserve the internal structure of your content:

```python
description = """Main description
    - Bullet point 1
    - Bullet point 2
        - Nested bullet
    - Bullet point 3"""

# Internal indentation and structure is preserved!
result = indent_multiline(description, 4)

# Output:
# Main description
#     - Bullet point 1
#     - Bullet point 2
#         - Nested bullet
#     - Bullet point 3
```

### 3. Empty Line Handling

Empty lines are preserved but not indented:

```python
text = """Paragraph 1

Paragraph 2"""

result = indent_multiline(text, 4)

# Output:
# Paragraph 1
#
# Paragraph 2
```

## API Reference

### `format_for_template(template: str, **kwargs) -> str`

Format a template string with automatic indentation detection for multi-line values.

**Parameters:**
- `template` (str): The template string with `{placeholder}` markers
- `**kwargs`: Key-value pairs to substitute into the template

**Returns:**
- str: Formatted string with proper indentation for all multi-line values

**Example:**
```python
template = """
Config:
    {settings}
End.
"""

settings = """debug: true
verbose: false
max_retries: 3"""

result = format_for_template(template, settings=settings)
# Auto-detects 4-space indent for settings
```

### `indent_multiline(text: str, indent: int = 0, indent_first: bool = False) -> str`

Dedent and re-indent multi-line text while preserving internal formatting.

**Parameters:**
- `text` (str): The multi-line text to process
- `indent` (int): Number of spaces to indent continuation lines
- `indent_first` (bool): If True, also indent the first line (default: False)

**Returns:**
- str: Properly indented text with internal formatting preserved

**Example:**
```python
text = """Line 1
    Nested line
    Another nested line"""

# Dedent and re-indent with 4 spaces
result = indent_multiline(text, 4)

# With first line indented
result = indent_multiline(text, 4, indent_first=True)
```

## Real-World Usage in Downes

### LLM Prompt Generation

The most common use case in Downes is formatting system prompts with tool descriptions:

```python
from downes.tools import TOOLS
from downes.utils import indent_multiline, format_for_template
from downes.prompts import PLANNING_SYSTEM_PROMPT

# Build tool descriptions with internal formatting
tool_descriptions = "\n\n".join([
    f"- {t.name}:\n  {indent_multiline(t.description, 2)}"
    for t in TOOLS
])

# Auto-format into the system prompt template
system_prompt = format_for_template(
    PLANNING_SYSTEM_PROMPT,
    tools=tool_descriptions
)
```

The template `PLANNING_SYSTEM_PROMPT` has:
```python
PLANNING_SYSTEM_PROMPT = """...
Available tools:
---
    {tools}
---
..."""
```

`format_for_template()` automatically detects the 4-space indentation and applies it to all tool descriptions.

### Other Use Cases

```python
# Task validation prompts
prompt = format_for_template(
    VALIDATION_PROMPT_TEMPLATE,
    task_desc=task_description,
    recent_results=results
)

# Answer generation
answer_prompt = format_for_template(
    ANSWER_TEMPLATE,
    query=user_query,
    all_results=collected_data
)

# Argument optimization
optimization_prompt = format_for_template(
    TOOL_ARGS_TEMPLATE,
    tool_description=tool.description,
    tool_schema=str(schema),
    initial_args=str(args)
)
```

## Benefits

### 1. No Manual Indentation Calculations

**Before:**
```python
# Had to count spaces manually
system_prompt = template.format(
    tools=indent_multiline(tool_descriptions, 4)  # Hardcoded!
)
```

**After:**
```python
# Automatic detection
system_prompt = format_for_template(template, tools=tool_descriptions)
```

### 2. Template-Agnostic Code

Change the template indentation without touching the code:

```python
# Change this:
template = """
Tools:
    {tools}    # 4 spaces
"""

# To this:
template = """
Tools:
  {tools}      # 2 spaces
"""

# Code remains the same - auto-detects the new indentation!
result = format_for_template(template, tools=descriptions)
```

### 3. Proper Markdown Formatting

LLM prompts maintain correct Markdown structure:
- Lists align properly
- Code blocks are formatted correctly
- Nested structures preserve their hierarchy

### 4. Reduced Errors

No more counting spaces or debugging misaligned output. The functions handle it automatically.

## Implementation Details

### How `format_for_template()` Works

1. **Parse the template** - Find all `{placeholder}` markers
2. **Detect indentation** - For each placeholder:
   - Extract the line containing the placeholder
   - Count leading whitespace
   - Check if placeholder is at start of line or inline
3. **Calculate indent amount**:
   - Block placeholder: Use line's leading whitespace count
   - Inline placeholder: Use column position of placeholder
4. **Apply indentation** - Call `indent_multiline()` with detected amount
5. **Format template** - Use standard `str.format()` with processed values

### How `indent_multiline()` Works

1. **Dedent** - Use `textwrap.dedent()` to remove common leading whitespace
2. **Split lines** - Process each line individually
3. **Preserve structure**:
   - First line: Optionally indent based on `indent_first` parameter
   - Continuation lines: Add indent while preserving their relative indentation
   - Empty lines: Preserve but don't indent
4. **Reconstruct** - Join lines and strip trailing whitespace

## Testing

Run the test suite:

```bash
# Test the utility functions
uv run python test_indent_multiline.py

# View demonstration
uv run python demo_indent_fix.py

# Verify integration with education tools
uv run python test_education_tools.py
```

## Migration Guide

### Upgrading Existing Code

**Old pattern:**
```python
system_prompt = TEMPLATE.format(
    tools=indent_multiline(tool_descriptions, 4),
    results=indent_multiline(results, 8),
    data=indent_multiline(data, 4)
)
```

**New pattern:**
```python
system_prompt = format_for_template(
    TEMPLATE,
    tools=tool_descriptions,
    results=results,
    data=data
)
```

### When to Use Each Function

**Use `format_for_template()`** when:
- Substituting into a template string
- You want automatic indentation detection
- Multiple placeholders need different indentation levels

**Use `indent_multiline()` directly** when:
- Building strings with f-strings (where placeholders are inline)
- You need precise control over indentation
- Working with non-template string operations

## Best Practices

### 1. Use `format_for_template()` for Templates

```python
# Good
prompt = format_for_template(TEMPLATE, **values)

# Avoid (unless you need manual control)
prompt = TEMPLATE.format(value=indent_multiline(value, 4))
```

### 2. Preserve Source Formatting

Write multi-line strings with their natural formatting:

```python
# Good - natural formatting
description = """
Main point
    - Bullet 1
    - Bullet 2
"""

# Avoid - pre-indented (defeats the purpose)
description = """    Main point
        - Bullet 1
        - Bullet 2"""
```

### 3. Use Docstrings as Source

Tool descriptions come from docstrings:

```python
@tool
def my_tool():
    """
    This is a tool description.

    Features:
        - Feature 1
        - Feature 2
    """
    pass

# The docstring formatting is preserved automatically
```

## Troubleshooting

### Issue: Text not indenting

**Cause:** Value is a single-line string

**Solution:** The functions only process multi-line strings (containing `\n`)

### Issue: Wrong indentation amount

**Cause:** Template placeholder positioning

**Solution:** Check the template structure:
```python
# Show exactly where the placeholder is
template_lines = template.split('\n')
for i, line in enumerate(template_lines):
    if '{placeholder}' in line:
        print(f"Line {i}: '{line}'")
        print(f"Indent: {len(line) - len(line.lstrip())} spaces")
```

### Issue: Internal formatting lost

**Cause:** Using `str.format()` instead of `format_for_template()`

**Solution:** Switch to `format_for_template()` or manually use `indent_multiline()`

## Future Enhancements

Potential improvements:

- Support for tab characters (currently assumes spaces)
- Configurable indent character (spaces vs tabs)
- Handling of complex nested templates
- Performance optimization for very large templates

## Related Documentation

- [F-String Multi-line Formatting Fix](./F_STRING_MULTILINE_FIX.md) - Original problem documentation
- [LLM Interaction Guide](./DEVELOPMENT_WORKFLOW.md) - How prompts are used in Downes
- [Verbose Debug Modes](./VERBOSE_DEBUG_MODES.md) - Debugging prompt formatting

## Summary

The auto-detecting indentation utilities solve a common Python string formatting challenge:

✅ **Automatic** - No manual indent calculations
✅ **Preserving** - Internal formatting maintained
✅ **Flexible** - Works with any indentation level
✅ **Reliable** - Thoroughly tested and production-ready

Use `format_for_template()` for all template string operations to get perfect formatting automatically!
