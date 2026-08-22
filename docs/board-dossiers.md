# Board Dossiers

Narration cut verbatim from TODO.md during register passes. Nothing here is
active work; see TODO.md for the live board.

## 2026-08-21 — Cut from TODO.md pre-opencode restructure

### Multi-Model LLM Routing (rationale, never started)

Plan how to run smaller and larger models side-by-side for different workflow stages.

### HyperTalk-Style Readability Improvements for agent.py (verbatim)

**Goal:** Make agent.py read like executable pseudo-code that non-programmers can understand.

**Key Principles:**
- Names should read like prose
- Functions should be commands or questions
- Code should read like a well-written instruction manual
- Make boolean conditions read as questions
- Use early returns instead of nested conditionals

**Specific Improvements to Consider:*r

1. **Natural Language Control Structures**
   - [ ] Replace `while action_count < max_steps_per_step` with `repeat_actions_for(step, maximum=...)`
   - [ ] Consider helper functions like `keep_working_on(step, until_condition)`

2. **Guard Clauses as Questions**
   - [ ] Convert `if limit_hit:` to `if we_have_exceeded_step_limit():`
   - [ ] Add `is_step_complete(ai_message)` instead of `not ai_message.tool_calls`
   - [ ] Use `are_we_in_a_loop(last_actions, new_action)` for readability

3. **Variable Names as Sentences**
   - [ ] Rename `step_history` → `what_we_learned_this_step`
   - [ ] Rename `run_history` → `everything_we_know_so_far`
   - [ ] Rename `action_count` → `how_many_attempts`
   - [ ] Rename `current_step` → `each_step` in loops

4. **Function Names as Imperatives/Commands (HyperTalk-style)**
   - [ ] `save_the_artifact()` → `put_result_in_vault()`
   - [ ] Consider `tell_logger_about(result)`, `ask_llm_what_to_do_next()`
   - [ ] Use `announce_step_start()`, `remember_success()`

5. **Named Constants with Context**
   - [ ] Define `REASONABLE_ATTEMPTS_PER_STEP = 5`
   - [ ] Define `SAFETY_LIMIT_FOR_TOTAL_ACTIONS = 20`

6. **Comments as Narration/Chapters**
   - [ ] Add chapter-style comments: `# === CHAPTER 1: Understanding What The User Wants ===`
   - [ ] Use narrative comments that explain the "why" not just the "what"

7. **Eliminate Nested Conditions**
   - [ ] Extract nested loops into `work_on_single_step(step, agent)` function
   - [ ] Use early returns with clear messaging
   - [ ] Flatten the main loop for better readability

8. **Domain-Specific Mini-Language**
   - [ ] Consider a `StepRunner` class with fluent interface: `.work_through(all_steps)`, `.complete(step)`
   - [ ] Add method chaining for readability

9. **State as a Story**
   - [ ] Create `RunningStory` class to collect scattered variables into narrative object
   - [ ] Properties: `original_question`, `everything_we_learned`, `current_chapter`, `why_we_stopped`

10. **Main Loop as Recipe**
    - [ ] Structure `run()` with clear recipe steps in docstring and implementation
    - [ ] Extract: `prepare_for_new_run()`, `ask_llm_to_make_plan()`, `work_on_step()`, `summarize_everything()`

11. **Error Handling as Conversation**
    - [ ] Create `try_to_run_tool()` that returns `(success, result_or_error_message)`
    - [ ] Add functions: `tell_user_it_worked()`, `apologize_for_failure()`

12. **Type Hints as Documentation**
    - [ ] Add type aliases: `UserQuery = str`, `StepDescription = str`, `WhatWeLearned = str`, `WhyWeStopped = str | None`
    - [ ] Use these in function signatures for self-documenting code

**References:**
- See detailed examples and code snippets in conversation history (2025-11-26)
- Goal: Make code understandable to non-programmers while maintaining functionality

## 2026-08-22 — Studio (v2 GUI) built + published

The Tauri studio (was "fog" backlog) was pulled forward and built end to
end. Both repos published to Sage-is (public): `AI-Education-Downes` (AGPL)
and `ai-ui-mini` (MIT fork, branch `downes/v1`), the fork tracked as a
submodule pinned to its HEAD.

Studio = Tauri v2 shell + opencode `serve` loopback sidecar + Solid/Vite
frontend. Three panes: Rust-fenced file manager (studio-rooted, plumbing
hidden, 2s live poll), the real branded TUI as a server PTY rendered in
xterm.js over a ticket-gated WebSocket, and a markdown/reveal artifact
viewer. See `ai-ui-mini/packages/studio/README.md`.

Bugs found and fixed, in order: (1) blank terminal — root cause was
frame handling, the server sends TUI OUTPUT as WebSocket string frames and
binary frames are 0x00 control frames; we cast everything to Uint8Array and
dropped the output. (2) engine load — xterm.css was a runtime dynamic
import() that rejected, killing createPty. (3) terminal review proved
opentui needs no special terminal (probes are fire-and-forget with
fallbacks), so xterm.js is the engine, behind a swappable adapter
(VITE_TERM_ENGINE). (4) V2 API wraps payloads as {location, data} — must
unwrap. (5) artifacts saved as flat root files — the path convention
demanded a timestamp the model can't generate; simplified to courses/<slug>/.
(6) file browser didn't refresh live — added a 2s poll. (7) links didn't
open — opener plugin needs a URL scope; replaced with a Rust open_external
command. (8) zoom didn't bind — zoomHotkeysEnabled inert on this macOS
webview; added Cmd +/-/0 → native setZoom. (9) CPU cooking — running the
TUI from source via bun idled ~34%+33%; compiling the fork binary and
running that dropped idle to ~15%+0.6%.

Open items surfaced: opentui idles ~15% even compiled (its own render loop,
upstream); artifact saving is prompt-driven not deterministic like the old
Python tool (nemotron followed the simplified convention; deepseek cleaner);
the opener plugin + 2 capabilities are now dead weight; the .gitignore
`studio/.downes/` rule silently ignores new files under it (narrow to
`studio/.downes/courses/`).
