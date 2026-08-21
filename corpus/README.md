# Regression corpus

Ten curated curriculum runs copied verbatim from `vault/`, tracked in git so
they survive `make things_clean` (`git clean -Xdf` cannot touch tracked
files). They are the structural baseline for the opencode-transition replay
harness (Gate 1, Gate 3 — see TODO.md).

## Contents

- `runs/<run-dir>/` — verbatim copies, vault naming preserved
  (`<YYYYMMDD_HHMMSS>_<slug>`, slug rules in `vault/README.md`).
- `manifest.json` — one entry per run: `prompt_reconstructed` (rebuilt from
  the dir slug — the original prompt is not stored anywhere in a run and
  slugs truncate at 50 chars), `task_list` (verbatim from `00_planning/`),
  and `expected` structure (step dirs, planning/summary presence, file
  count).
- Validated by `scripts/validate_corpus.py` (stdlib only): naming contract,
  structure drift, file counts. CI runs it on every push.

## Selection criteria

Coverage over volume: every education tool appears in at least two runs —
full 8-step pipelines (grade-8 maker, oral-health, grade-9 english), single
tools (sailing slides), search/verify-heavy runs (sage.education, youtube
research), an assessments/quiz run, and one trivial baseline
(`say-hello-to-the-class`) that mirrors the one-line test's shape.

## Adding a run

Copy the run dir from `vault/` into `runs/`, regenerate the manifest entry
(structure fields must match exactly), and run
`python3 scripts/validate_corpus.py` before committing. Keep the corpus
under ~4 MB; the full 34-run modern set stays in `vault/` for
`make replay_full`.
