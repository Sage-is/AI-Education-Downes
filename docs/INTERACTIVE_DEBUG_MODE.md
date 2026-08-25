# Interactive Debug Mode

The agent now features an **interactive debug mode** that allows you to review, edit, and approve every LLM prompt before it's submitted. This gives you complete control over the agent's behavior and enables prompt engineering experimentation.

## Features

### 🔍 Prompt Preview
Before each LLM call, see:
- The operation name (e.g., "Task Planning", "Action Planning", "Answer Generation")
- The complete system prompt
- The complete user prompt

### ✏️ Interactive Editing
For each prompt, you can:
- **Submit as-is** - Send the prompt unchanged
- **Edit user prompt** - Modify the user-facing prompt
- **Edit system prompt** - Modify the system instructions
- **View full prompts** - See complete, untruncated prompts
- **Cancel** - Skip this LLM call entirely

### 📝 Editor Integration
Prompts open in your system editor:
- Respects `$EDITOR` environment variable
- Falls back to `$VISUAL` if `$EDITOR` not set
- Defaults to `nano` if neither is set
- Works with any text editor (vim, emacs, VS Code, etc.)

## Usage

### Enable Interactive Debug Mode

```bash
# Run with debug flag
uv run downes-agent --debug "Create a Python course"

# Or use short form
uv run downes-agent -d "Design a math curriculum"

# Via environment variable
DOWNES_DEBUG=true uv run downes-agent "Build a science module"
```

### Interactive Workflow

When debug mode is active, before each LLM call you'll see:

```
────────────────────────────────────────────────────────────────────────────────
📝 PROMPT PREVIEW: Task Planning
────────────────────────────────────────────────────────────────────────────────

[SYSTEM PROMPT]
You are an expert curriculum developer specializing in creating engaging...

[USER PROMPT]
Project: "Create a 6-week Python course for high school students"
Create a list of curriculum development tasks to be completed...

────────────────────────────────────────────────────────────────────────────────

Options:
  [s] Submit as-is
  [e] Edit user prompt
  [E] Edit system prompt
  [v] View full prompts
  [c] Cancel (skip this LLM call)

Your choice [s]:
```

### Option Details

#### Submit as-is `[s]`
- Press `s` or just hit Enter
- Sends the prompt to the LLM unchanged
- Continues normal execution

#### Edit User Prompt `[e]`
- Opens the user prompt in your editor
- Modify as needed, save, and close
- Updated prompt is shown for review
- You can submit, edit again, or cancel

#### Edit System Prompt `[E]`
- Opens the system prompt in your editor
- Allows changing agent behavior/instructions
- Updated prompt is shown for review
- Useful for prompt engineering experiments

#### View Full Prompts `[v]`
- Displays complete, untruncated prompts
- Helpful for long prompts
- Returns to menu after viewing

#### Cancel `[c]`
- Skips this LLM call
- Agent handles gracefully (returns None)
- May affect downstream operations
- Useful for testing error handling

## Examples

### Basic Usage

```bash
# Start agent in debug mode
uv run downes-agent --debug "Create a course on data structures"

# First prompt appears (Task Planning)
# Press 's' to submit
# Press 'e' to edit user prompt
# Press 'E' to edit system prompt
# Press 'v' to view full prompts
# Press 'c' to cancel
```

### Changing Your Editor

```bash
# Use vim
EDITOR=vim uv run downes-agent -d "Design a curriculum"

# Use VS Code
EDITOR=code uv run downes-agent -d "Plan a course"

# Use emacs
EDITOR=emacs uv run downes-agent -d "Build a module"

# Set permanently in your shell profile
export EDITOR=vim  # Add to ~/.bashrc or ~/.zshrc
```

### Prompt Engineering Workflow

1. **Run in debug mode** to see default prompts
2. **View full prompts** to understand current approach
3. **Edit prompts** to test improvements
4. **Submit and observe** the LLM's response
5. **Iterate** on different prompt variations

### Cancelling Operations

If you want to skip an LLM call:

```
Your choice [s]: c
Are you sure you want to cancel this LLM call? (y/N): y
✗ LLM call cancelled

[DEBUG] Task Planning - CANCELLED BY USER
```

The agent will continue but handle the missing response appropriately.

## Use Cases

### 1. Prompt Development
Test and refine prompts before committing to code:
```bash
uv run downes-agent -d "Test query"
# Edit prompts to test different approaches
# Find optimal phrasing
# Document successful patterns
```

### 2. Debugging Issues
Diagnose unexpected behavior:
```bash
uv run downes-agent -d "Problematic query"
# Review what prompt is actually being sent
# Check if context is included correctly
# Verify system instructions are appropriate
```

### 3. Educational Exploration
Learn how the agent works:
```bash
uv run downes-agent -d "Simple query"
# See how queries are decomposed
# Understand the planning process
# Learn prompt engineering techniques
```

### 4. Cost Control
Prevent expensive LLM calls:
```bash
uv run downes-agent -d "Complex query"
# Review prompts before submission
# Cancel calls that seem redundant
# Optimize prompt length
```

### 5. Experimentation
Try different approaches:
```bash
uv run downes-agent -d "Experiment query"
# Edit system prompt to change behavior
# Try different instruction styles
# Test various context formats
```

## Technical Details

### Implementation

The interactive prompt review is implemented in `src/downes/llm_interaction.py`:

```python
def _review_and_edit_prompt(
    prompt: str,
    system_prompt: str,
    operation_name: str,
    logger: Logger,
) -> tuple[str, str]:
    """Allow user to review and optionally edit prompts before submission."""
    # Display preview
    # Show interactive menu
    # Handle user choice
    # Return edited or original prompts
```

### Editor Integration

```python
def _edit_text_in_editor(text: str, title: str = "Edit") -> str:
    """Open text in system editor for editing."""
    editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
    # Create temp file with prompt
    # Open in editor
    # Read back changes
    # Clean up temp file
```

### Integration Points

Every `call_llm_safe()` invocation checks for debug mode:

```python
if debug:
    prompt, system_prompt = _review_and_edit_prompt(
        prompt, system_prompt, operation_name, logger
    )

    if prompt is None or system_prompt is None:
        logger._log(f"[DEBUG] {operation_name} - CANCELLED BY USER")
        return None
```

### Operation Names

Each LLM call has a descriptive operation name:
- **Task Planning** - Decomposing query into tasks
- **Task Planning (Retry)** - Retry with clarification
- **Action Planning** - Deciding next tool to use
- **Task Validation** - Checking if task is complete
- **Goal Validation** - Checking if overall goal achieved
- **Argument Optimization** - Refining tool parameters
- **Answer Generation** - Creating final response

## Best Practices

### 1. Start with View
When learning, use `[v]` to view full prompts first:
```
Your choice [s]: v
# Read the complete prompts
# Understand the context
# Then decide to submit or edit
```

### 2. Edit Iteratively
Make small, incremental changes:
```
Your choice [s]: e
# Make one change
# Submit and observe
# Iterate based on results
```

### 3. Document Findings
Keep track of what works:
```bash
# Run with debug and capture output
uv run downes-agent -d "Query" > debug_log.txt 2>&1
# Review successful prompts
# Note effective patterns
```

### 4. Use Cancellation Wisely
Cancel when:
- The prompt looks incorrect
- You want to skip redundant calls
- Testing error handling
- Conserving API costs

### 5. Combine with Verbose Mode
See both prompts and performance:
```bash
uv run downes-agent --debug --verbose "Query"
# Interactive prompt editing
# Plus timing and token usage
```

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `s` or Enter | Submit | Send prompt as-is |
| `e` | Edit User | Modify user prompt |
| `E` | Edit System | Modify system prompt |
| `v` | View Full | See complete prompts |
| `c` | Cancel | Skip this LLM call |

## Troubleshooting

### Editor Won't Open

Check your environment:
```bash
# Verify EDITOR is set
echo $EDITOR

# Set if needed
export EDITOR=nano  # or vim, code, etc.

# Test the editor
$EDITOR test.txt
```

### Prompts Not Appearing

Ensure debug mode is active:
```bash
# Verify flag is set
uv run downes-agent --debug "Query"  # Not just -v

# Or use environment variable
DOWNES_DEBUG=true uv run downes-agent "Query"
```

### Can't Save Changes in Editor

Make sure you know the editor:
- **nano**: Ctrl+O to save, Ctrl+X to exit
- **vim**: `:wq` to save and quit
- **emacs**: Ctrl+X Ctrl+S to save, Ctrl+X Ctrl+C to quit
- **VS Code**: Cmd+S to save, close tab when done

## Related Documentation

- [VERBOSE_DEBUG_MODES.md](./VERBOSE_DEBUG_MODES.md) - Verbose and debug mode overview
- [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) - Development practices
- Main README.md - General usage

## Testing

Test the interactive features:

```bash
# Run interactive test
python test_interactive_prompts.py

# Test with real agent
uv run downes-agent -d "Test query"
```

## Future Enhancements

Potential improvements:
- Save/load prompt templates
- Prompt history and reuse
- Diff view for edited prompts
- Batch edit mode for multiple prompts
- Prompt validation and syntax checking
- Integration with prompt libraries
