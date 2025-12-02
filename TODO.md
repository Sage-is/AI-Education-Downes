# TODO: AI-Education-Downes

## 🔥 This Week (November 12, 2025)

### 🔥 Architecture Simplification: Markdown-First Refactoring

**Status:** In Progress  
**Goal:** Eliminate JSON complexity and embrace Markdown as the native output format

**Rationale:**

- LLMs excel at generating clean, structured Markdown
- JSON schemas add unnecessary complexity (prompting, validation, coercion)
- Markdown is human-readable, making vault artifacts more accessible
- Follows project principles: DRY, KISS, less is more
- Built-in support for lists, checklists, headings, code blocks

**Tasks:**

- [x] Create TODO.md with simplification plan
- [x] Update education tools to return Markdown
- [x] Simplify vault.py for Markdown-first storage

### Fix and optimize tools

- [x] Fix curate learning resources to not break the urls obtained from searxng by grounding outputs in parsed SearXNG hits and preserving original links.

### ⏭️ Upcoming: Multi-Model LLM Routing

Plan how to run smaller and larger models side-by-side for different workflow stages.

- [ ] Expand env config to support named LLM profiles (fast/standard/premium) with dedicated keys, base URLs, and temps.
- [ ] Update `get_llm_config`/`call_llm` to accept a profile parameter plus helper routing logic per task type.
- [ ] Tag each tool/agent flow with an appropriate profile (e.g., planning → premium, drafting → fast) and expose CLI flags for overrides.
- [ ] Add tests plus README/env.example docs covering multi-profile setup and fallback behavior.

### 🛠️ Tooling & UX

- [ ] Evaluate how to auto-generate the "what's possible" message in the intro based on available tools (dynamic tool discovery).

### 📖 HyperTalk-Style Readability Improvements for agent.py

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

---

## Previous Weeks

### Completed Work

Completed work will be moved here in reverse chronological order.
