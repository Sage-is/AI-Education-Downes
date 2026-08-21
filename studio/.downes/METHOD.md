# The Downes method (CP0 stub)

You work inside the studio — this folder. Courses live in `courses/`.

- One course = one folder: `courses/<YYYYMMDD_HHMMSS>_<slug>/`. The slug is
  the request, lowercased, `\/*?:"<>|` stripped, whitespace collapsed to
  single hyphens, at most 50 characters.
- Before writing any artifact, write `00_plan.md` in the course folder: the
  steps you intend to take, one line each. Plan, document, execute, verify.
- Then execute every step of that plan in the same run, without stopping to
  ask. A course request is not done until every artifact the plan names
  exists — finishing the plan file is the beginning of the work, not the end.
- Artifacts are Markdown files named for what they are: `objectives.md`,
  `syllabus.md`, `assessments.md`, `pacing.md`, `taxonomy.md`,
  `resources.md`, `slides.md`, `worksheet.md`. `README.md` summarizes the
  finished course.
- Everything must open cleanly in Obsidian. No JSON artifacts.
- Use the curriculum skills for their steps; do not improvise formats they
  already define.

(Full METHOD lands at Checkpoint 1.)
