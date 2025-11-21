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

---

## Previous Weeks

### Completed Work

Completed work will be moved here in reverse chronological order.
