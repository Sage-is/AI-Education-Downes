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
  output contract exactly: `01_objectives.md` requires the
  learning-objectives skill; `02_syllabus.md` requires the syllabus skill;
  `07_slides.md` requires the slide-deck skill.
  An artifact written without loading its skill is invalid and must be
  redone — never improvise a format a skill already defines.

(Full METHOD lands at Checkpoint 1.)
