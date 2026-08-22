# The Downes method

You work inside the studio — this folder. Courses live in `courses/`.

- **Every curriculum artifact is written to a file — never delivered only
  inline.** This holds even for a single-artifact request ("Build a rubric
  for grade 7 emotional regulation", "Draft objectives for X"). Make a
  course folder, load the artifact's skill, and write the artifact to its
  `NN_` file (a lone rubric → `03_assessments.md`). Do the research in the
  chat if you must, but the deliverable itself lands as a file. In the TUI
  reply, give only a short pointer ("Wrote `03_assessments.md` — open it on
  the right"), not the full artifact pasted inline. If you find yourself
  about to print a whole rubric/objective list/syllabus into the
  conversation, stop and write it to the course folder instead.

The full pipeline order is: objectives → syllabus → assessments → pacing →
taxonomy → resources → slides → worksheet. Not every request needs all
eight — a slides request needs only objectives and slides — but the steps
a course does use run in this order, because later artifacts consume
earlier ones.

- One course = one folder: `courses/<YYYYMMDD_HHMMSS>_<slug>/`. The slug is
  the request, lowercased, `\/*?:"<>|` stripped, whitespace collapsed to
  single hyphens, at most 50 characters.
- **Clarifying questions: at most one, interactive only, never blocking.**
  - In an interactive session (the TUI, where a person is at the keyboard),
    you may ask ONE upfront clarifying question when an unstated choice
    would materially change the course — the audience, say. Ask it once,
    then build.
  - In a single-shot run (headless, `opencode run`), there is no one to
    answer: never ask. A terse prompt ("draft a slideshow on sailing") is a
    complete instruction.
  - Either way, a missing input is never a reason to stop. Choose sensible
    defaults from each skill for anything unstated — audience, level,
    duration, counts — and record those assumptions in the first lines of
    `00_plan.md`. Build the course; never leave it unbuilt waiting for a
    reply.
- Before writing any artifact, write `00_plan.md` in the course folder: the
  assumptions you chose, then the steps you intend to take, one line each.
  Plan, document, execute, verify.
- Then execute every step of that plan in the same run, without stopping to
  ask. A course request is not done until every artifact the plan names
  exists — finishing the plan file is the beginning of the work, not the end.
- Artifacts are Markdown files with fixed `NN_` number prefixes that carry
  the pipeline order: `00_plan.md`, `01_objectives.md`, `02_syllabus.md`,
  `03_assessments.md`, `04_pacing.md`, `05_taxonomy.md`, `06_resources.md`,
  `07_slides.md`, `08_worksheet.md`, then `90_research.md` and
  `99_summary.md`. The numbers are fixed per artifact type — a course that
  skips a step leaves a gap, never renumbers.
- `90_research.md` is the research log, and it records ONLY searches you
  actually executed with the websearch tool in this run — the query, the
  results the tool returned, URLs verbatim as returned. Before writing
  `06_resources.md`, run websearch; if search is unavailable or you ran
  none, the log must contain exactly one line: "No searches were run — all
  resources below are [Unverified]." Anything cited in `06_resources.md`
  must appear in the log first.
- **[Verified] is earned, never asserted.** A source is [Verified] only
  after you fetched it with webfetch in this run. When webfetch is
  unavailable, every source is [Unverified], no exceptions. Never write a
  date you did not observe; omit dates rather than inventing them.
  A fabricated URL, date, or [Verified] tag is a broken course, not a
  cosmetic flaw.
- `99_summary.md` wraps up the finished course: what was built, for whom,
  and how to use the folder.
- Everything must open cleanly in Obsidian. No JSON artifacts.
- **Skills are mandatory for their artifacts.** Before writing an artifact
  whose skill exists, load that skill with the skill tool and follow its
  output contract exactly: `01_objectives.md` → learning-objectives ·
  `02_syllabus.md` → syllabus · `03_assessments.md` → assessments ·
  `04_pacing.md` → pacing-guide · `05_taxonomy.md` → taxonomy-map ·
  `06_resources.md` → learning-resources · `07_slides.md` → slide-deck ·
  `08_worksheet.md` → worksheet.
  An artifact written without loading its skill is invalid and must be
  redone — never improvise a format a skill already defines.

Before finishing, verify: every artifact the plan names exists, every
mandatory skill was loaded, every cited URL is in the research log, and
`99_summary.md` reflects what was actually built.
