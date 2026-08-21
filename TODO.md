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

## In Progress

- [ ] **Gate 0 — repo transition ready** #task
  - [x] Makefile scaffold commit (68a36bd)
  - [ ] register pass commit
  - [ ] corpus commit
  - [ ] CI commit
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
  - [ ] pin `opencode/big-pickle`, `nemotron-3.5-lightning-free` fallback
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
