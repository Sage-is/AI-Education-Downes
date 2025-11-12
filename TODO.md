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
- [ ] Remove Pydantic schemas (schemas.py)
- [ ] Simplify model.py (remove output_schema parameter)
- [ ] Update all prompts to request Markdown instead of JSON
- [ ] Refactor agent.py to parse Markdown instead of JSON
- [ ] Update education tools to return Markdown
- [ ] Simplify vault.py for Markdown-first storage
- [ ] Update tests to expect Markdown output
- [ ] Update documentation (README, workflow docs)

---

## Previous Weeks

**Completed work will be moved here in reverse chronological order**
