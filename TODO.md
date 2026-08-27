# Downes — Chart

> Navigate chart, top → down.
> Decisions land under `docs/decisions/`.
> Narration in `docs/dossiers/` (internal, not in git — see
> `docs/internal-docs.md`), stubs in `docs/completed-todos.md`.

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

Long-form narration behind these cards is internal and lives in
`docs/dossiers/` — outside git, carried to the team by repo backup/sync.
Cards here state the work; they do not restate the reasoning.

## Delivered (engineering done; human gates still pending)

- [x] **Studio (v2 GUI)** — Tauri shell + opencode `serve` sidecar + Solid
  frontend; branded TUI in xterm over a PTY WS; file manager + artifact
  viewer; zoom, drag-panes, external links; compiled-binary perf. See
  `ai-ui-mini/packages/studio/README.md`. (was fog backlog)
- [x] 8 skills + METHOD + persona; harness (`corpus.jsonl`, `assertions.py`,
  `replay.py`); Make targets; CI (offline blocking + nightly live).
- [x] Launcher isolation (XDG_CONFIG_HOME + OPENCODE_CONFIG + OPENCODE_PURE);
  legal matrix (no RED); brew formula + unsigned-DMG path.
- [x] **Studio branding + theming** — real app icon (Sage.is hex-S, Downes
  gradient) replacing the stock Tauri logo; startr.style vendored (CSP blocks
  its CDN); tokens aligned to Sage.is AI-UI; light/dark toggle on `data-theme`
  following system by default; terminal repaints with the theme.
- [x] Fork branded on `downes/v1`; `launcher/downes.sb` sandbox wired into the
  launcher, engine-level escape test ALL GREEN, `make sandbox_test` in CI.
  Prerequisite shipped with it: per-product `XDG_*` state roots, so the engine
  keeps auth and its database inside the studio rather than the shared
  `~/.local/share/opencode` every product wrote to.

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
  - [ ] profile it: frame-timer or event-driven? file the upstream issue rather than accepting by default

- [ ] **A teacher uses it, on the record** #task — no verbatim teacher
  feedback exists yet; staff and client teachers are available now
  - [ ] one real course, one real class, friction logged verbatim

- [ ] **Ship on Homebrew (Phase −1)** #task — self-contained payload, no
  Gatekeeper warning, no Apple account needed. Plan: `~/.claude/plans/`
  - [x] engine resolution is install-relative (`engine_bin()` walks up from `current_exe()`)
  - [x] launcher + `Downes.app` shim find the engine under the brew layout
  - [x] `scripts/package_macos.sh` builds a self-contained tarball (49 MB, verified with bun/node/opencode off PATH)
  - [x] formula rewritten: per-arch, real sha256, working install block
  - [ ] publish the GitHub release + push the formula to `Sage-is/homebrew-apps`
  - [ ] Intel build (needs an x86_64 CI runner; formula `odie`s honestly for now)

- [ ] **Studio cleanups** #task
  - [ ] remove the dead opener plugin + 2 capabilities (links use `open_external`)
  - [ ] narrow `.gitignore` `studio/.downes/` → `studio/.downes/courses/` (it silently ignores new files under `.downes`)
  - [ ] compiled binary into packaging/CI (dev builds it ad hoc)

## Decision cards

- [ ] **Skill licence** #interview — recommendation recorded (fork MIT in
  `ai-ui-mini`, this repo AGPL); ratify at Gate 4
- [ ] **Windows sandbox** #research — v1 ships no OS containment; recorded in
  `docs/decisions/windows-sandbox.md`
- [ ] **Linux containment** #research — unclaimed. Landlock is the light
  option (kernel 5.13+, unprivileged, inherited across `exec`); the launcher
  leaves the seam. Ladder recorded in `docs/decisions/vm-containment.md`
- [ ] **Per-harness state roots** #task — `XDG_*` isolation fixed the opencode
  collision; pi and deepseek each arrive with their own store
  - [ ] convention is `$STUDIO/.downes/harness/<name>/`; nothing enforces it yet
- [ ] **Pinned Zen model** #prototype — nemotron pinned; deepseek best format
  discipline; formal judgment via replay when the tier allows
- [ ] **searx_search hosting** #research — curated SearXNG as the durable
  allowlist lock, or stay on websearch + domain allowlist
- [ ] **Fork rebase cadence** #task — monthly timed drill onto upstream ≤~20 min
- [ ] **Python plumbing retention** #interview — Blocked by Gate 3; default is
  removal, keep only with a named consumer

## Backlog

- [ ] **Prompt-injection surface** #interview — course files are untrusted
  input; nothing stops instructions inside a downloaded curriculum steering
  the agent. Dossier 2026-08-23
  - [ ] treat curriculum files as data, never instructions to follow word for word
  - [ ] re-isolate auth/XDG in a locked teacher mode; relaxed full-auth mode stays the dev opt-in
  - [ ] revisit right after the application demo
- [ ] **Restore the teacher interview** #interview — the back-and-forth that
  made the output the teacher's own is missing from the loop. Dossier
  2026-08-23
  - [ ] restore dialogue; longer where judgment lives (sequencing, assessment choice), skipped for formatting
  - [ ] harness scores a dialogue-free course as FAILED, not fast
  - [ ] the agent must be able to disagree and hold the position
- [ ] **Invert the access ladder** #interview — easiest tier inherits any of
  130 models; the tier with the most pedagogical discipline needs the hardest
  setup. Easy should mean opinionated, advanced configurable. Dossier
  2026-08-23
  - [ ] mini ships a hosted Sage default; the full model picker becomes the advanced opt-in
  - [ ] same build as the locked teacher mode — hermetic auth, one model, no configuration
  - [ ] surface which model is in use; silent agreement is an invisible failure
- [ ] **Sycophancy test in the corpus** #prototype — add a deliberately bad
  pedagogy prompt (timed multiple-choice for creative writing); PASS only when
  the agent refuses. Run across the picker, publish the results
- [ ] **Notarized DMG** — Apple Developer, Developer ID, notarytool + staple;
  v1 ships brew tap + unsigned DMG
- fog: Sage gateway (api.sage.is), allowlist proxy for host-pinning, corpus
  growth, Obsidian polish, wterm/ghostty engine swap, startr.style in the viewer

## Out of scope

- Multi-model routing — superseded by opencode native model config.
- HyperTalk agent.py readability — superseded; narration in `docs/dossiers/`.
- Intro auto-generation — superseded by native skill discovery.

## Done

- [x] Markdown-First Refactoring — stub at `docs/completed-todos.md`
- [x] SearXNG URL preservation fix — stub at `docs/completed-todos.md`
