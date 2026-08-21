# Downes — Chart

> Navigate chart, top → down.
> Decisions land under `docs/decisions/`.
> Narration in `docs/board-dossiers.md`, stubs in `docs/completed-todos.md`.

## Destination

Downes ships as Markdown skills on opencode 1.18.18 on the Sage.is AI-UI mini
platform; this repo stays the curriculum-asset home. Teacher pilot (Gate 4)
says ship.

## Notes

RAD rules: advisor reviews after every checkpoint, go/no-go at every gate,
CI on commit, one-line test green daily, timeboxes ÷20 agent-crewed.

CP0 gate note (2026-08-21): GREEN — one-line test passed all six checks
(exit 0, course folder with all 8 artifacts, structure greps, skill tool
fired 2×, zero "openai" anywhere, posture probes hold: bash refused, /tmp
write denied, studio write allowed). Config deltas vs the briefing, all in
studio/opencode.json: sage provider stripped (NXDOMAIN) · `{file:}` prompt
syntax · mcp deferred (no downes-mcp binary) · deck command deferred to CP1 ·
autoupdate false during delivery · webfetch deny (ask auto-rejects and kills
non-interactive runs; websearch works and stays) · provider whitelist pins
the picker to 2 free models (Zen otherwise exposes 20 gpt-* entries) ·
agent steps 60 · model pinned nemotron-3.5-lightning-free (see Pinned Zen
model card). Harness env: OPENCODE_DISABLE_EXTERNAL_SKILLS=1 so a dev
machine's ~/.claude skills stay out of the studio.

CP0 review findings (Alexander, 2026-08-21), both fixed and re-proven green:
(1) NN_ artifact numbering was lost — METHOD now fixes numbers per artifact
type (00_plan … 08_worksheet, 90_research, 99_summary; gaps allowed, never
renumber). (2) Search results were invisible — 90_research.md is now the
research log holding verbatim websearch output; and one run FABRICATED the
entire log (fake queries, dates, URLs, [Verified] tags, zero websearch
calls) — METHOD now forbids [Verified] without a webfetch in-run, forbids
invented dates, and requires the log to record only tool-executed searches.
Third finding while fixing: runs sometimes skip the skill tool and
improvise formats — skills are now mandatory per artifact in METHOD, and
the CP1 harness hard-gates skill-not-fired, fabricated URLs, and false
[Verified] tags. Zen flake note: one run died provider-side mid-pipeline
(zero-token completion, exit 0) — the harness retry rule stands.

## In Progress

- [ ] **Gate 0 — repo transition ready** #task
  - [x] Makefile scaffold commit (68a36bd)
  - [x] register pass commit (4124fe0)
  - [x] corpus commit (b5e7a57)
  - [x] CI commit — offline blocking + nightly live; test_providers.py deleted
  - [ ] advisor review
  - [ ] record `docs/decisions/gate-0-repo-ready.md`

## TODO

- [ ] **Gate 1 — skills extracted, no regressions** #task — Blocked by Gate 0
  - [ ] author `downes.md`, `METHOD.md`, and all 8 SKILL.md files (Passes 1–3)
  - [ ] harness `corpus.jsonl` + `assertions.py` (all 34 runs, 10 subset)
  - [ ] `scripts/replay.py` — hermetic tempdir studio, hard gates + advisory overlap
  - [ ] Make targets `validate_config` / `replay` / `replay_full` / `studio_test` / `ci`
  - [ ] advisor review: replay 10/10 subset, ≥31/34 full corpus, written triage
  - [ ] stage-1 Python removal; tag `pre-opencode`

- [ ] **Gate 2 — launcher + legal** #task — Blocked by Gate 0 (runs parallel to Gate 1)
  - [ ] `docs/legal/STATUS_MATRIX.md` — GREEN/AMBER/RED, no RED, licence recommendation recorded
  - [ ] `launcher/downes.sh` — `OPENCODE_CONFIG_DIR`, XDG under `.downes/xdg/`, disable project config + autoupdate
  - [ ] Keychain-gated Sage key (`is.sage.downes`), Zen `public` as the floor
  - [ ] first-launch bootstrap + `Downes.app` shim (unsigned in v1; signing backlogged)
  - [ ] advisor review: `debug paths` inside studio, antigravity grep = 0, user db untouched

- [ ] **Gate 3 — contained + installable** #task — Blocked by Gate 2
  - [ ] fork `ai-ui-mini` @ v1.18.18 — `brand.ts` + 8-file brand surface, LICENSE byte-identical
  - [ ] timed rebase drill onto v1.18.19 ≤ ~20 min
  - [ ] `launcher/downes.sb` deny-default sandbox + escape test + in-anger OS-layer test
  - [ ] brew tap `sage-is/tap/downes` clean-account install + unsigned DMG
  - [ ] advisor review: fork diff scoped, escape tests green
  - [ ] work the Python plumbing retention card

- [ ] **Gate 4 — teacher pilot ship/no-ship** #task — Blocked by Gate 3
  - [ ] author `docs/pilot/PILOT_NOTES_TEMPLATE.md` + `GATE-4-CHECKLIST.md` mapped to DoD
  - [ ] pilot: unaided brew install, one-line test, one authentic class task
  - [ ] Obsidian open + navigate, export/share artifact, 15-min debrief
  - [ ] checklist green + advisor sign-off; record `docs/decisions/gate-4-ship.md`
  - [ ] `make minor_release` → v1.0.0

### Decision cards

- [ ] **Skill licence** #interview — AGPL/dual; fork lives in a separate MIT repo
  - [ ] record recommendation: platform repo MIT + upstreamable patches, this AGPL repo stays the curriculum home
  - [ ] matrix rows GREEN/AMBER/RED with Blocks ∈ {prototype, pilot, launch}

- [ ] **Windows sandbox** #research — v1 ships no OS containment
  - [ ] record decision: "works in one folder" wording, exportable artifacts
  - [ ] AppContainer only if demand materialises

- [ ] **Pinned Zen model** #prototype — Blocked by Gate 2
  - [x] CP0 evidence: big-pickle failed the one-line test 3× (ends turn mid-plan); nemotron-3.5-lightning-free completed the full 8-artifact pipeline — pinned as model, big-pickle kept as small_model
  - [ ] formal judgment via corpus replay at Gate 2
  - [ ] replay distinguishes provider flake from regression

- [ ] **searx_search hosting** #research
  - [ ] curated SearXNG instance as the durable allowlist lock for grounded websearch
  - [ ] port grounded `learning-resources` mode (L258) to native `websearch`

- [ ] **Fork rebase cadence** #task
  - [ ] monthly timed rebase drill onto upstream, target ≤ ~20 min
  - [ ] maintain the patch series (`git format-patch v1.18.18..downes/v1`)

- [ ] **Python plumbing retention** #interview — Blocked by Gate 3
  - [ ] weigh what of the LLM layer stays post-parity; default is removal
  - [ ] whatever stays needs a named consumer and stays green in CI

## Backlog

- [ ] **Notarized DMG distribution** — Apple Developer enrollment, Developer ID, notarytool + staple; v1 ships brew tap + unsigned DMG
- fog: Tauri GUI with startr.style + startr.swap, Sage gateway api.sage.is, allowlist proxy, corpus growth, Obsidian polish

## Out of scope

- Multi-model routing — superseded by opencode native model config.
- HyperTalk agent.py readability — superseded; narration preserved in `docs/board-dossiers.md`.
- Intro auto-generation — superseded by native skill discovery.

## Done

- [x] Markdown-First Refactoring — stub at `docs/completed-todos.md`
- [x] SearXNG URL preservation fix — stub at `docs/completed-todos.md`
