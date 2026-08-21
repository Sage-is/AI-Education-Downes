---
name: syllabus
description: Draft a module-by-module course syllabus aligned to learning objectives. Use when the user asks for a syllabus, course outline, or module plan — normally after learning-objectives has produced objectives.md.
---

# Drafting a syllabus

## Inputs to gather (ask if missing)

- course_title (required) · learning_objectives (read `01_objectives.md` if
  present) · duration_weeks (required) · modality (default: in-person)
- prerequisites (optional) · modules_count (default: 4)

## Method

You are a curriculum designer. Draft a concise module-by-module syllabus outline using `### Module X: Title` headings in order. For each module include:

- A 1-2 sentence summary
- Bullet list of 2-3 aligned objectives pulled or remixed from the provided
  list
- Bullet list of signature learning activities
- A single formative or summative assessment idea

Keep the tone practical and avoid extra commentary outside the requested structure.

## Output contract

Write `02_syllabus.md` in the current course folder. 
The file must contain only, in this order:

```markdown
# <Course Title> - Syllabus

## Course Information

- **Duration:** <N> weeks
- **Modality:** <Modality>

### Prerequisites        <!-- only when prerequisites exist -->

- <prerequisite>

## Course Modules

### Module 1: <Title>
...
```

Modules are numbered `### Module 1:` through `### Module <modules_count>:`.
