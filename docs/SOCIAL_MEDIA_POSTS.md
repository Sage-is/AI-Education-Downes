# Social Media Posts - Auto-Detecting Indentation Feature

## Twitter/X Posts

### Post 1 - Problem Introduction (280 chars)

```
🐍 Python developers: Ever struggled with multi-line strings in f-strings?

The first line looks great, but subsequent lines lose their indentation, breaking your carefully crafted Markdown formatting.

We solved this in our AI education agent. Thread 🧵👇
```

### Post 2 - The Problem (280 chars)

```
The issue: When you substitute a multi-line variable into an f-string, only the first line respects the horizontal position.

```python
prompt = f"""
    {description}
"""
# Line 2+ start at column 0 😱
```

This breaks Markdown formatting in LLM prompts.
```

### Post 3 - The Solution (280 chars)

```
Our solution: `format_for_template()`

It automatically detects where each placeholder appears in your template and applies the correct indentation to ALL lines.

No more manual space counting!

```python
format_for_template(template, tools=descriptions)
```

✨ Magic ✨
```

### Post 4 - Key Features (280 chars)

```
What makes it special:

✅ Auto-detects indentation (no hardcoded values)
✅ Preserves internal formatting (bullets, nesting)
✅ Handles both inline & block placeholders
✅ Works with any template structure

Template-agnostic code that just works.
```

### Post 5 - Code Example (280 chars)

```
Before: Manual indentation 😓
```python
prompt = TEMPLATE.format(
    tools=indent_multiline(tools, 4),
    data=indent_multiline(data, 8)
)
```

After: Auto-detection 🎉
```python
prompt = format_for_template(
    TEMPLATE, tools=tools, data=data
)
```

Clean & simple!
```

### Post 6 - Call to Action (280 chars)

```
Building AI agents with complex prompts? This utility can save you hours of formatting headaches.

⭐ Check out our open-source education agent: github.com/Sage-is/AI-Education-Downes

Full docs: [link to repo]/docs/AUTO_INDENT_FORMATTING.md

#Python #AI #DevTools
```

---

## LinkedIn Post (Long Form)

```
🚀 Solving Python's Multi-line String Formatting Challenge

When building our AI education agent (Downes), we encountered a common but frustrating problem: multi-line string substitution in f-strings and templates.

THE PROBLEM 😓

When you substitute a multi-line variable into a template, Python only positions the first line correctly. Subsequent lines start at column 0, breaking your carefully structured output:

```python
description = """Line 1
Line 2
Line 3"""

prompt = f"""
    Tool: {description}
"""

# Output:
#     Tool: Line 1
# Line 2
# Line 3
```

This is especially problematic when generating Markdown-formatted LLM prompts where proper indentation is critical for readability and structure.

THE SOLUTION ✨

We built two utilities that solve this elegantly:

1️⃣ indent_multiline() - Manually control indentation while preserving internal formatting

2️⃣ format_for_template() - Automatically detect and apply the correct indentation

The game-changer is the auto-detection. Our function analyzes the template to determine where each placeholder appears, then applies the exact indentation needed—no manual calculations required.

BEFORE:
```python
system_prompt = TEMPLATE.format(
    tools=indent_multiline(tool_descriptions, 4),  # Manual!
    results=indent_multiline(results, 8),
    data=indent_multiline(data, 4)
)
```

AFTER:
```python
system_prompt = format_for_template(
    TEMPLATE,
    tools=tool_descriptions,
    results=results,
    data=data
)
```

KEY BENEFITS:

✅ Template-agnostic - Change template indentation without touching code
✅ Preserves structure - Bullets, nesting, and formatting maintained
✅ Zero configuration - Works automatically with any template
✅ Error-free - No more counting spaces or debugging misalignment

REAL-WORLD IMPACT:

In our education agent, this processes tool descriptions with complex nested formatting:

- Tool name
  - Description line 1
      - Nested bullet
      - Another nested bullet
  - Description line 2

Everything aligns perfectly in the final prompt, making our LLM interactions more reliable and our code more maintainable.

This is part of our open-source AI Education Agent (Downes), built to help educators design curricula through conversational AI.

🔗 Check it out: github.com/Sage-is/AI-Education-Downes
📖 Full documentation: [repo]/docs/AUTO_INDENT_FORMATTING.md

Have you faced similar string formatting challenges in Python? How did you solve them? Would love to hear your approaches in the comments! 💬

#Python #SoftwareEngineering #AI #OpenSource #DeveloperTools #CleanCode
```

---

## Dev.to / Medium Article Title & Intro

### Title
**Auto-Detecting Indentation for Python Multi-line Strings: A Template Formatting Solution**

### Subtitle
*How we solved f-string indentation issues in our AI agent with automatic placeholder detection*

### Opening Paragraph

```
If you've ever worked with multi-line strings in Python f-strings or templates, you've likely encountered this frustrating issue: the first line of your substituted variable appears at the correct horizontal position, but every subsequent line stubbornly starts at column zero. This breaks Markdown formatting, creates misaligned output, and requires tedious manual indentation calculations.

While building Downes, an AI-powered education agent for curriculum design, we faced this problem repeatedly when constructing complex LLM prompts. Our system prompts needed to include tool descriptions with nested bullet points, code examples, and structured Markdown—all requiring precise indentation.

We solved it with an elegant utility that automatically detects template placeholder positions and applies the correct indentation. Here's how we did it, and how you can use it in your own projects.
```

---

## Reddit Posts

### r/Python

**Title:** [OC] Auto-detecting indentation for multi-line string formatting in Python

**Body:**
```
I built a utility to solve the common problem of multi-line variable substitution in f-strings and templates.

**The Problem:**
When you substitute a multi-line variable into a template, only the first line respects the horizontal position. This breaks formatting, especially for Markdown in LLM prompts.

**The Solution:**
`format_for_template()` automatically detects where each placeholder appears in your template and applies the correct indentation to all continuation lines.

```python
# Before
prompt = TEMPLATE.format(tools=indent_multiline(tools, 4))

# After
prompt = format_for_template(TEMPLATE, tools=tools)
```

Key features:
- Auto-detects indentation (no hardcoded values)
- Preserves internal formatting (bullets, nesting, etc.)
- Works with any template structure
- Handles both inline and block placeholders

Built this for our open-source AI education agent. Thought it might be useful to others!

GitHub: [repo link]
Docs: [docs link]

Would love feedback or suggestions for improvements!
```

### r/learnpython

**Title:** TIL: How to properly indent multi-line strings in f-string templates

**Body:**
```
Wanted to share a solution to a formatting problem I kept running into.

When you have a multi-line string that you want to substitute into an f-string, the continuation lines don't inherit the indentation:

```python
description = """Line 1
Line 2"""

output = f"""
    Description: {description}
"""

# You get:
#     Description: Line 1
# Line 2  <- Not indented!
```

I wrote a utility function that automatically detects the indentation and fixes this:

```python
from my_utils import format_for_template

template = """
    Description: {description}
"""

output = format_for_template(template, description=description)

# Now you get:
#     Description: Line 1
#                  Line 2  <- Properly indented!
```

The function analyzes the template to figure out where the placeholder is and applies the right amount of indentation automatically.

Full implementation here: [link]

Hope this helps someone else struggling with the same issue!
```

---

## Hacker News

**Title:** Auto-detecting indentation for Python template strings

**Submission Text:**
```
While building an AI agent for curriculum design, we kept running into issues with multi-line string formatting in Python templates. When substituting multi-line variables into f-strings or str.format() templates, continuation lines would lose their indentation.

We solved this with a utility that automatically detects where placeholders appear in the template and applies the correct indentation—no manual calculations needed.

The approach: parse the template to find each placeholder's position, calculate its indentation context (block vs. inline), then apply that indentation to all continuation lines while preserving the content's internal structure.

It's template-agnostic, so you can change your template's indentation without touching the code. Works particularly well for generating structured LLM prompts with Markdown formatting.

Open source as part of our education AI agent: [repo link]
Technical docs: [docs link]
```

---

## YouTube Video Script Outline

**Title:** Python String Formatting: Auto-Detecting Indentation for Multi-line Templates

**Hook (0:00-0:15):**
"Have you ever struggled with this in Python? You substitute a multi-line string into an f-string, and everything looks perfect... except it doesn't. Let me show you what I mean and how to fix it automatically."

**Problem Demo (0:15-1:30):**
- Live coding example showing the broken formatting
- Visual highlighting of misalignment
- Explain why this happens

**Solution Introduction (1:30-2:00):**
- Introduce format_for_template()
- Show the clean API

**How It Works (2:00-4:00):**
- Explain the detection algorithm
- Show code walkthrough
- Demonstrate with different indentation levels

**Real-World Example (4:00-5:30):**
- Show the LLM prompt use case
- Before/after comparison
- Explain the benefits

**Call to Action (5:30-6:00):**
- GitHub repo link
- Documentation
- Ask for comments/suggestions

---

## GitHub Repository Updates

### README.md Addition

```markdown
## 🎯 Key Features

### Auto-Detecting String Indentation

Downes includes smart utilities for handling multi-line string formatting in Python templates:

```python
from downes.utils import format_for_template

# Automatically detects and applies correct indentation
system_prompt = format_for_template(
    TEMPLATE,
    tools=tool_descriptions,
    data=results
)
```

Perfect for generating properly formatted LLM prompts with complex nested structures. [Learn more →](docs/AUTO_INDENT_FORMATTING.md)
```

### CHANGELOG.md Entry

```markdown
## [Unreleased]

### Added
- **Auto-detecting indentation utilities** for multi-line string formatting
  - `format_for_template()` - Automatically detects placeholder indentation in templates
  - `indent_multiline()` - Manual control over multi-line text indentation with structure preservation
  - Solves f-string formatting issues for LLM prompts and Markdown generation
  - See [documentation](docs/AUTO_INDENT_FORMATTING.md) for details
```

---

These social media posts cover different platforms and audiences, from technical deep-dives to quick tips, ensuring maximum reach and engagement!
