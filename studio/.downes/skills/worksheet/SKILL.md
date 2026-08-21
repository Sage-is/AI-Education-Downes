---
name: worksheet
description: Design a printable, classroom-ready student worksheet with differentiation tiers and an answer key. Use when the user asks for a worksheet, handout, or practice activity, or when a course plan names 08_worksheet.md.
---

# Designing a worksheet

## Inputs to gather (ask if missing)

- topic (required) · audience (required) · skill_focus (required)
- estimated_time_minutes (default: 30) · materials (default: Pencil, Notebook)
- sections (default: Warm-Up Prompt, Guided Practice, Apply & Create)
- differentiation_tiers (default: All Learners, Needs Support, Ready for More)
- include_answer_key (default: yes) · learning_objectives (read
  `01_objectives.md` if present)

## Method

You create printable worksheets for educators using Markdown. Structure
requirements:

1. Title slide style header: `# Worksheet: <topic>`.
2. Overview block that lists audience, skill focus, estimated time, and
   materials as bullets.
3. One section per provided label with `## <Section>` heading containing:
   one sentence of framing text; 2-3 numbered tasks or prompts aligned to
   objectives; an optional mini-table or checklist when it strengthens
   clarity.
4. Include a `### Differentiation` section with one bullet per tier that
   explains how to adapt a task.
5. If an answer key is requested, end with `### Answer Key` summarizing
   expected responses.
6. Avoid extra commentary, YAML, or fenced code blocks.
7. Keep tone encouraging and directions student-facing.

## Output contract

Write `08_worksheet.md` in the current course folder, containing only the
worksheet per the structure above — header, overview, sections,
`### Differentiation`, `### Answer Key`.
