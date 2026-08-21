---
name: pacing-guide
description: Create a week-by-week pacing guide allocating hours across modules. Use when the user asks for pacing, scheduling, or time allocation, or when a course plan names 04_pacing.md.
---

# Creating a pacing guide

## Inputs to gather (ask if missing)

- duration_weeks (required) · modules_count (read `02_syllabus.md` if
  present) · hours_per_week (default: 5)

## Method

Build the weekly allocation table yourself, deterministically: modules map
onto weeks in order, hours split across Content, Practice, and Assessment.
Then write the highlights as a pacing guide expert: concise Markdown bullet
points describing the instructional focus for each week, in the format
`- **Week N (Module M):** <focus sentence>`. Mention signature activities
or checkpoints when helpful and ensure every week appears exactly once.

## Output contract

Write `04_pacing.md` in the current course folder. The file must contain
only, in this order:

```markdown
## Pacing Guide

| Week | Module | Total Hours | Content | Practice | Assessment | Focus |
|------|--------|-------------|---------|----------|------------|-------|
... one row per week ...

### Weekly Highlights

- **Week 1 (Module 1):** <focus sentence>
...
```

The table columns are exactly the seven shown, and every week appears in
both the table and the highlights.
