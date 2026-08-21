---
name: assessments
description: Design assessments with rubrics aligned to each learning objective. Use when the user asks for assessments, quizzes, rubrics, or evaluation, or when a course plan names 03_assessments.md.
---

# Designing assessments

## Inputs to gather (ask if missing)

- learning_objectives (read `01_objectives.md` if present; required)
- types (default: project, quiz, presentation, reflection)
- rubric_scale, top to bottom (default: Exemplary, Proficient, Developing, Beginning)

## Method

You are an assessment designer. For each provided learning objective, craft a
matching assessment concept. Format strictly in Markdown with the pattern:

```markdown
### Assessment N: <Assessment Type>
**Aligned Objective:** ...
**Assessment Summary:** ...
| Level | Descriptor |
|-------|------------|
... one row per rubric level ...
```

Include 3 criteria bullets (Skills Demonstrated, Evidence of Mastery,
Feedback Focus). Use only the provided rubric scale ordering and vary
assessment types within the suggested set. Every assessment must carry a
criteria table with `Criterion` and `Weight` columns.

## Output contract

Write `03_assessments.md` in the current course folder. The file must open
with:

```markdown
## Assessments & Rubrics

Aligned assessments for each learning objective:
```

followed by one `### Assessment N:` block per objective, in objective
order, and nothing else.
