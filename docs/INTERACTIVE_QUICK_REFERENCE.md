# Interactive Debug Mode - Quick Reference

## When to Use

✅ **Use Interactive Debug Mode when you want to:**
- Review prompts before they're sent to the LLM
- Experiment with prompt engineering
- Understand how the agent constructs queries
- Debug unexpected behavior
- Control costs by reviewing/cancelling calls
- Learn how the system works internally

## The Interactive Menu

Every time the agent is about to call the LLM, you'll see:

```
────────────────────────────────────────────────────────────────────────────────
📝 PROMPT PREVIEW: Task Planning
────────────────────────────────────────────────────────────────────────────────

[SYSTEM PROMPT]
You are an expert curriculum developer...
(truncated preview shown)

[USER PROMPT]
Create a 6-week course on Python programming...
(truncated preview shown)

────────────────────────────────────────────────────────────────────────────────

Options:
  [s] Submit as-is
  [e] Edit user prompt
  [E] Edit system prompt
  [v] View full prompts
  [c] Cancel (skip this LLM call)

Your choice [s]:
```

## Option Guide

### [s] Submit (Default)
Just press Enter or type 's'
- Sends the prompt unchanged
- Continues normal execution
- Quickest option

### [e] Edit User Prompt
Opens your editor with the user prompt
- Modify the query/context
- Save and close to see updated preview
- Can edit multiple times

### [E] Edit System Prompt
Opens your editor with the system instructions
- Change agent behavior
- Experiment with instructions
- Test different approaches

### [v] View Full
Shows complete prompts without truncation
- See everything being sent
- Returns to menu after
- Good for long prompts

### [c] Cancel
Skips this LLM call entirely
- Confirms before cancelling
- Agent handles gracefully
- Useful for cost control

## Quick Tips

1. **Default to Submit**: Press Enter to keep moving
2. **View First**: Use `v` when learning to see full context
3. **Edit Iteratively**: Make small changes and test
4. **Cancel Wisely**: Skip redundant or incorrect calls
5. **Set Your Editor**: `export EDITOR=vim` (or code, emacs, etc.)

## Example Session

```bash
# Start in debug mode
$ uv run downes-agent --debug "Create a Python course"

# First call: Task Planning
[s]: ⏎                    # Submit, looks good
✓ Submitting prompt...

# Second call: Action Planning
[e]: ⏎                    # Edit user prompt
# (editor opens, make changes)
✓ User prompt updated

[s]: ⏎                    # Submit modified prompt

# Third call: Tool Arguments
[v]: ⏎                    # View full prompts first
# (reads full context)

[s]: ⏎                    # Submit after review

# Fourth call: Redundant?
[c]: ⏎                    # Cancel this one
Are you sure? y
✗ LLM call cancelled
```

## Common Workflows

### Learning Mode
```
Query -> [v] View -> [s] Submit -> Observe -> Repeat
```

### Development Mode
```
Query -> [e] Edit -> Test -> [E] Edit System -> Test -> [s] Submit
```

### Production Mode
```
Query -> [s] Submit -> [s] Submit -> [s] Submit (fast-forward through)
```

### Cost Control Mode
```
Query -> [v] Review -> [c] Cancel if redundant -> [s] Submit important ones
```

## Environment Setup

```bash
# Set your preferred editor
export EDITOR=nano        # Simple, beginner-friendly
export EDITOR=vim         # Powerful, modal editing
export EDITOR=code        # VS Code (--wait flag added automatically)
export EDITOR=emacs       # Extensive customization

# Add to shell profile for persistence
echo 'export EDITOR=vim' >> ~/.bashrc   # bash
echo 'export EDITOR=vim' >> ~/.zshrc    # zsh
```

## Keyboard Tips

**In the menu:**
- Type option letter + Enter
- Or just Enter for default [s]
- Ctrl+C to interrupt (like cancel)

**In nano editor:**
- Ctrl+O to save
- Ctrl+X to exit

**In vim:**
- Press `i` to insert/edit
- Press Esc then `:wq` to save & quit
- Press Esc then `:q!` to quit without saving

**In VS Code:**
- Cmd/Ctrl+S to save
- Close tab when done
- Agent waits for you to close

## Integration with Other Tools

Combine with other agent features:

```bash
# Interactive debug + verbose metrics
uv run downes-agent -d -v "Query"

# Save session with all prompts
uv run downes-agent -d "Query" > session.log 2>&1

# Experiment with different models
MODEL=gpt-4 uv run downes-agent -d "Query"
```

## Troubleshooting

**Menu not appearing?**
- Check you used `--debug` not just `--verbose`
- Verify: `uv run downes-agent --debug "test"`

**Editor not opening?**
- Set EDITOR: `export EDITOR=nano`
- Test: `$EDITOR test.txt`
- Check VISUAL as backup: `export VISUAL=nano`

**Changes not reflected?**
- Make sure you saved in the editor
- Check for error messages
- Try viewing with [v] to confirm

**Want to skip interactive?**
- Use `--verbose` instead of `--debug`
- Or script responses: `yes s | uv run downes-agent -d "Query"`

## Best Practices

✅ **Do:**
- Start with [v] when unfamiliar
- Make small edits and test
- Cancel obviously redundant calls
- Document successful prompt patterns
- Use for learning and development

❌ **Don't:**
- Edit every single prompt (slows things down)
- Make large prompt changes without understanding
- Cancel critical calls (may break flow)
- Forget to save in editor
- Skip reading the preview

## Next Steps

- Read [INTERACTIVE_DEBUG_MODE.md](./INTERACTIVE_DEBUG_MODE.md) for full details
- Try [test_interactive_prompts.py](../test_interactive_prompts.py) for a demo
- Review [VERBOSE_DEBUG_MODES.md](./VERBOSE_DEBUG_MODES.md) for other debug features
- Check [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) for development tips
