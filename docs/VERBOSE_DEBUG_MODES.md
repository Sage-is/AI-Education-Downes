# Verbose and Debug Modes

The Agent now supports **verbose** and **debug** modes to control visibility of LLM interactions and improve transparency during execution.

## Quick Start

### Command Line Flags

```bash
# Normal mode (default - quiet operation)
uv run downes

# Verbose mode (shows LLM timing and token usage)
uv  run downes-agent --verbose
uv  run downes-agent -v

# Debug mode (shows detailed LLM prompts, responses, and traces)
uv  run downes-agent --debug
uv  run downes-agent -d

# Both modes together
uv  run downes-agent --verbose --debug
uv  run downes-agent -v -d

# Show help
uv  run downes-agent --help
```

### Environment Variables

```bash
# Enable verbose mode via environment variable
DOWNES_VERBOSE=true uv run downes

# Enable debug mode via environment variable
DOWNES_DEBUG=true uv run downes

# Both modes
DOWNES_VERBOSE=true DOWNES_DEBUG=true uv run downes
```

## What Each Mode Shows

### Normal Mode (Default)
- Clean, minimal output
- Progress spinners for long operations
- Task completion status
- Final answer display

### Verbose Mode (`--verbose` or `-v`)
- All normal mode output
- LLM API call timing
- Token usage statistics (prompt, completion, total)
- Connection retry information
- No spinners in debug contexts

### Debug Mode (`--debug` or `-d`)
- All verbose mode output
- Full system prompts (truncated to 200 chars)
- User prompts sent to LLM (truncated to 500 chars)
- LLM responses (truncated to 500 chars)
- Tool call counts
- Tool execution details with arguments and results
- Operation names for each LLM interaction
- Disables progress spinners for cleaner debug output

## Code Improvements

### DRYer Code Structure

The refactoring includes:

1. **Unified LLM Calling**: Single `_call_llm_safe()` method with comprehensive error handling and logging
2. **Progress Control**: Conditional progress display based on debug mode
3. **Operation Tracking**: All LLM calls tagged with operation names for debugging
4. **Reusable Patterns**: Common patterns extracted into helper methods
5. **Configuration Propagation**: Verbose/debug flags flow through all components

### Key Changes

#### Agent Class (`agent.py`)
- Added `verbose` and `debug` parameters to constructor
- Enhanced `_call_llm_safe()` with operation naming and debug logging
- Split decorated methods into public/private pairs for conditional progress display
- Added debug logging to tool execution

#### Model Layer (`model.py`)
- Added `verbose` parameter to `call_llm()`
- Timing and token usage logging
- Connection retry visibility

#### UI Layer (`ui.py`)
- Enhanced `show_progress()` decorator with `enabled` parameter
- Spinners can be disabled for debug mode

#### CLI (`cli.py`)
- Argument parsing for `--verbose`, `-v`, `--debug`, `-d`
- Environment variable support
- Help text display

## Examples

### Example Output (Verbose Mode)

```
[LLM] Calling gpt-4.1...
[LLM] Response received in 1.23s
[LLM] Tokens - Prompt: 450, Completion: 120, Total: 570
```

### Example Output (Debug Mode)

```
============================================================
[DEBUG] Task Planning
[SYSTEM PROMPT]
You are an expert curriculum developer...

[USER PROMPT]
Given the user query: "Create a 6-week course on Python"...

[RESPONSE]
- [ ] Generate learning objectives for Python course
- [ ] Draft syllabus outline with 6 modules...

[TOOL CALLS] 2 call(s)
============================================================

[TOOL EXECUTION] generate_learning_objectives with args: {'topic': 'Python', 'grade_level': 'college'}
[TOOL RESULT] ## Learning Objectives for Python...
```

## Testing

Test the modes with:

```bash
# Run mode tests
uv run python test_verbose_modes.py

# Run full test suite with verbose output
DOWNES_VERBOSE=true uv run python test_education_tools.py
```

## Benefits

1. **Transparency**: See exactly what prompts are being sent to the LLM
2. **Cost Monitoring**: Track token usage in real-time
3. **Performance Analysis**: Measure LLM response times
4. **Debugging**: Identify issues with prompts or responses
5. **Learning**: Understand how the agent processes queries
6. **Production Ready**: Clean output by default, detailed logging when needed

## Integration

When using the Agent programmatically:

```python
from downes.agent import Agent

# Default mode
agent = Agent()

# Verbose mode
agent = Agent(verbose=True)

# Debug mode
agent = Agent(debug=True)

# Both modes
agent = Agent(verbose=True, debug=True)

# Run with query
result = agent.run("Create a Python course")
```

## Performance Impact

- **Normal mode**: No impact
- **Verbose mode**: Minimal impact (adds timing and token logging)
- **Debug mode**: Slight impact due to additional string operations and I/O

The debug output is written to stdout and can be redirected:

```bash
# Save debug output to file
uv  run downes-agent --debug > debug.log 2>&1
```
