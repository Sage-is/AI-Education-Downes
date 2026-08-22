# Downes — Chart

> Navigate chart, top → down.
> Decisions land under `docs/decisions/`.
> Narration in `docs/board-dossiers.md`, stubs in `docs/completed-todos.md`.

## Destination

Downes ships as Markdown skills on opencode 1.18.18, running on the Sage.is
AI-UI mini platform; this repo stays the curriculum-asset home. Teacher
pilot (Gate 4) says ship.

## Notes

RAD rules: advisor reviews after every checkpoint, go/no-go at every gate,
CI on commit, one-line test green daily, timeboxes ÷20 agent-crewed.

Published 2026-08-22: both repos public on Sage-is — `AI-Education-Downes`
(AGPL, this repo) and `ai-ui-mini` (MIT fork, branch `downes/v1`), the fork
tracked here as a **submodule**. Fresh clones need `--recurse-submodules`.

CP0 gate note + review findings and the full 2026-08-22 studio build/fix
narration live in `docs/board-dossiers.md`.

## Delivered (engineering done; human gates still pending)

- [x] **Studio (v2 GUI)** — Tauri shell + opencode `serve` sidecar + Solid
  frontend; branded TUI in xterm over a PTY WS; file manager + artifact
  viewer; zoom, drag-panes, external links; compiled-binary perf. See
  `ai-ui-mini/packages/studio/README.md`. (was fog backlog)
- [x] 8 skills + METHOD + persona; harness (`corpus.jsonl`, `assertions.py`,
  `replay.py`); Make targets; CI (offline blocking + nightly live).
- [x] Launcher isolation (XDG_CONFIG_HOME + OPENCODE_CONFIG + OPENCODE_PURE);
  legal matrix (no RED); brew formula + unsigned-DMG path.
- [x] Fork branded on `downes/v1`; `launcher/downes.sb` sandbox + escape test
  ALL GREEN + in-anger OS-layer fail.

## In Progress / TODO

- [ ] **Gate reviews** #task — the human go/no-go at each gate is the only
  thing between "built" and "signed off"
  - [ ] advisor reviews G0–G3 (artifacts + CI links per DoD)
  - [ ] record `docs/decisions/gate-{0,1,2,3}-*.md`

- [ ] **Gate 1 — replay parity number** #task — Blocked by tier/route
  - [~] subset replay root-caused (terse-prompt halt, fixed 3c5aa9c) — see dossier
  - [ ] clean 10/10 subset + ≥31/34 full run — BLOCKED on free-tier throughput; needs tier recovery or Sage/paid route
  - [ ] then tag `pre-opencode`; stage-1 Python removal

- [ ] **Gate 4 — teacher pilot** #task — Blocked by Gate 3 sign-off
  - [ ] author `docs/pilot/PILOT_NOTES_TEMPLATE.md` + `GATE-4-CHECKLIST.md`
  - [ ] pilot: brew install, one authentic task, Obsidian, export, debrief
  - [ ] checklist green; record `docs/decisions/gate-4-ship.md`; v1.0.0

- [ ] **Artifact-save reliability** #interview — saving is prompt-driven, not
  deterministic like the old Python tool
  - [ ] nemotron followed `courses/<slug>/` after the timestamp was dropped; deepseek was cleaner — decide the shippable model, or add a deterministic write hook

- [ ] **opentui idle CPU** #research — ~15% even compiled (its own render
  loop); upstream throttle or accept

- [ ] **Studio cleanups** #task
  - [ ] remove the dead opener plugin + 2 capabilities (links use `open_external`)
  - [ ] narrow `.gitignore` `studio/.downes/` → `studio/.downes/courses/` (it silently ignores new files under `.downes`)
  - [ ] compiled binary into packaging/CI (dev builds it ad hoc)

## Decision cards

- [ ] **Skill licence** #interview — recommendation recorded (fork MIT in
  `ai-ui-mini`, this repo AGPL); ratify at Gate 4
- [ ] **Windows sandbox** #research — v1 ships no OS containment; recorded in
  `docs/decisions/windows-sandbox.md`
- [ ] **Pinned Zen model** #prototype — nemotron pinned; deepseek best format
  discipline; formal judgment via replay when the tier allows
- [ ] **searx_search hosting** #research — curated SearXNG as the durable
  allowlist lock, or stay on websearch + domain allowlist
- [ ] **Fork rebase cadence** #task — monthly timed drill onto upstream ≤~20 min
- [ ] **Python plumbing retention** #interview — Blocked by Gate 3; default is
  removal, keep only with a named consumer

## Backlog

- [ ] **Match sage.is AI-UI styling** #task — align the studio chrome (palette, type, components) with the real Sage.is AI-UI design system; startr.style + startr.swap in the viewer
- [ ] **Notarized DMG** — Apple Developer, Developer ID, notarytool + staple;
  v1 ships brew tap + unsigned DMG
- fog: Sage gateway (api.sage.is), allowlist proxy for host-pinning, corpus
  growth, Obsidian polish, wterm/ghostty engine swap, startr.style in the viewer

## Out of scope

- Multi-model routing — superseded by opencode native model config.
- HyperTalk agent.py readability — superseded; narration in `docs/board-dossiers.md`.
- Intro auto-generation — superseded by native skill discovery.

## Done

- [x] Markdown-First Refactoring — stub at `docs/completed-todos.md`
- [x] SearXNG URL preservation fix — stub at `docs/completed-todos.md`
