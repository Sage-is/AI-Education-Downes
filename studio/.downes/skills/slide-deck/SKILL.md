---
name: slide-deck
description: Generate a reveal.js-ready Markdown slide deck for a lesson or talk. Use when the user asks for slides, a deck, a presentation, or when a course plan names 07_slides.md.
---

# Building a slide deck

## Inputs to gather (ask if missing)

- topic (required) · audience (required) · duration_minutes (default: 45)
- slide_count (default: 8) · learning_objectives (read `01_objectives.md`
  if present) · include_notes (default: yes) · tone (default: approachable)

## Method

You are an instructional designer who writes Reveal.js Markdown slide decks.
Rules:

- Start with a title slide containing `# Title` and key metadata as a bullet
  list or subheading.
- Separate slides using a line that contains only `---` and a blank line
  after it.
- Each content slide must start with `## Slide Title`.
- Include short bullet lists or concise paragraphs only; keep each slide
  under 60 words.
- When notes are requested, add a blank line followed by `Notes:` and a
  short presenter note.
- Mirror the provided slide sections and learning objectives succinctly.

## Output contract

Write `07_slides.md` in the current course folder. The file must contain
only the deck itself — reveal.js-ready Markdown, no commentary, no triple
backticks around the deck, nothing before the title slide or after the last
slide. Shape:

```markdown
# <Title>

- <audience> · <duration> min

---

## <Slide Title>

- <point>
- <point>

Notes: <presenter note>

---
```

A file with zero `---` separator lines is not a slide deck and fails the
contract.
