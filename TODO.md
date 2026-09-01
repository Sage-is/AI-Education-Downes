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
- [x] Fork branded on `downes/v1`; `launcher/downes.sb` wired on both surfaces —
  `launcher/downes.sh` and the studio sidecar (`lib.rs:sandbox_prefix`).
  22-case escape test ALL GREEN on a machine with an engine; the macOS CI job
  runs the profile cases only, since a clean runner has no engine to fence.
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

- [ ] **mini workspace is ~/SAGE.ISmini** #task — SHIPPED 2026-09-01 in v0.1.8
  - [x] renamed at the source (`product` marker), so launcher and studio agree
  - [x] migration carries ~/SageMini across on first run, both entry points;
    verified from a real tap install with a seeded courses/ file
  - [x] cask zaps both names so an upgrade-then-uninstall leaves nothing
  - [ ] hand-off to the team: `brew upgrade --cask mini`

- [ ] **v0.1.7 — the 0.1.6 fix pass** #task — SHIPPED 2026-09-01 as a
  pre-release on both repos, tap at 0.1.7. Three of four defects fixed and
  verified on a real install; the crash loop is contained, not cured
  - [x] **crash loop — ROOT CAUSE FOUND 2026-09-01**, and it was never the
    installed app. Spotlight was launching the BUILD-TREE bundle at
    `target/release/bundle/macos/SAGE.IS mini.app`, whose `Contents/Resources`
    holds only `icon.icns` — no engine, no launcher, no `product` marker
    - [x] with no bundled engine, `engine_bin()` returns empty, so both the
      sidecar and `createPty` take the bun-from-source branch rooted at
      `fork_opencode()`, which walked up from the INHERITED cwd into
      `~/Documents/...` — a tree `downes.sb` denies outright. Hence the EPERM
      lstat on the repo root, the dying pane, and "sidecar unreachable"
    - [x] fix 1: `fork_opencode()` walks up from `current_exe()`, never the cwd,
      matching the rule the file already states at line 75
    - [x] fix 2: the app sets its cwd to the studio before anything else runs,
      so nothing inherited can leak
    - [x] fix 3: unregistered the stale and build-tree bundles from Launch
      Services; Spotlight now offers only `/Applications/SAGE.IS mini.app`
    - [x] a bundle with no engine now says so plainly instead of probing
    - [x] **the actual cause, found 2026-09-01 in the engine's environment:**
      `PWD` still held the launching shell's directory. `set_current_dir()` and
      `Command::current_dir()` change the real cwd but NEVER update `PWD`, and
      Node and Bun read `PWD` in preference to `getcwd()`. So the engine stat'd
      the repo no matter what its actual cwd was. Fixed by setting `PWD`
      alongside every cwd change: app startup, sidecar spawn, and the PTY child
    - [x] the engine-less-bundle theory was WRONG, or at most a second path to
      the same symptom — 0.1.9 still failed on a clean tap install. Do not
      re-derive it: check `ps -Eww` for `PWD` first
  - [x] **respawn guard** — `Terminal.tsx` counts panes that die inside 5s,
    backs off exponentially to 15s, and after 5 gives up naming the command it
    ran; `createPty` returns that command so the banner can print it
    - [x] first attempt measured on a real install: 23 cycles at a FLAT 2.8s,
      no backoff. `recover()` reset the counter on a successful spawn, and a
      spawn succeeds even when the child dies right after, so the cap was
      unreachable. `ws.onclose` now owns the only reset, and only for a pane
      that actually lived
    - [x] re-measured on 0.1.7: stops at exactly 5, spaced +3.0s, +4.8s, +8.8s,
      +15.9s, then gives up naming the command
  - [x] **hardcoded dev path** — the `fork_opencode()` fallback now returns an
    empty `PathBuf`, which fails the downstream `is_file()` checks honestly.
    It used to name the maintainer's own checkout and shipped that to every user
  - [x] **sidecar orphan** — root cause found by testing, not by reading. The
    handle we hold is `sandbox-exec`; the engine is its child and puts ITSELF
    in a fresh process group (observed PGID == its own PID), so neither
    `child.kill()` nor a group signal reached it. First attempt (own process
    group) was verified and FAILED. Now reaps by parent pid via `pkill -P`,
    wired to `RunEvent::Exit` as well as window-destroyed so Cmd-Q is covered.
    Verified on 0.1.7 and 0.1.8: nothing survives a normal quit
    - [ ] LIMIT, measured: a SIGTERM to the GUI still orphans the engine, since
      Tauri's exit event never fires. Cmd-Q, the menu and closing the window are
      all covered; `kill` is not. Needs a signal handler to close fully
  - [x] **edit permissions** — see the card below; Downes fixed and tested
  - [ ] gate: verify on a second Mac. Still the open question — this machine is
    the one where that hardcoded path existed, and 0.1.7 removed it, so a
    teammate launch now tests a genuinely different binary
  - [ ] stays pre-release until the pane stops exiting 1

- [ ] **Edit permissions never match; folders do not line up** #task — proven
  2026-09-01, blocks a clean teacher run on both products. In the 0.1.7 pass
  - [ ] `edit.ts:104` matches a path RELATIVE to the worktree, while
    `permission/index.ts:186` expands `~/Downes/**` to ABSOLUTE — never matches
  - [ ] Downes: only `"*": "deny"` matches, so the agent is denied by its own
    `studio/opencode.json`
  - [ ] mini ships no `opencode.json` at all and falls to the default `ask` —
    this is the prompting teachers hit
  - [ ] name is wrong for mini too: rules say `~/Downes`, workspace is `~/SageMini`
  - [ ] `"**": "allow"` is NOT the fix — it matches `../.ssh/id_rsa`; containment
    stays `external_directory` plus the Seatbelt profile
  - [x] Downes fixed: `studio/opencode.json` now allows `courses/**` and
    `.downes/**` — worktree-relative, so they match what `edit.ts` passes and
    work for any workspace name. Verified against the real `Wildcard` matcher:
    3 in-studio paths allow, 4 escapes (`../.ssh/id_rsa`, `../../../etc/passwd`,
    a keychain, and `opencode.json` itself) deny
  - [ ] mini still prompts BY DESIGN: it has no folder convention to allow-list,
    and no safe blanket exists (`**` matches `../.ssh/id_rsa`). It now at least
    ships `external_directory: deny` instead of no config at all
  - [ ] decide mini's model — a convention to allow-list, or accept prompting

- [ ] **Week 7 notebook PRs** #task — three submissions, none in `week-7/`
  - [x] #3 and #4 commented 2026-09-01 with the exact `git mv`; they followed
    the convention as it stood when they branched, so this is not their error
  - [ ] waiting on the contributors to push; merge once week-7/ is the path
  - [x] #2 moved on develop to `notebooks/week-7/isabelle.ipynb`
  - [x] discarded the unpushed local rename branch `hkarim-10/develop`
  - [ ] `~` in `hanna_~_week_7.ipynb` is the one real defect: shells expand it

- [ ] **`--version` reports the engine stamp, not the release** #task — a
  teacher checking their version sees `0.0.0-downes/v1-202608271608`, not 0.1.6
  - [ ] the side-effect half is fixed in 0.1.6; only the string is wrong now

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
  - [x] publish the GitHub release + push the formula to `Sage-is/homebrew-apps`
    (v0.1.3 / mini-v0.1.3, 2026-08-27; `brew upgrade` verified from the tap)
  - [ ] Intel build (needs an x86_64 CI runner; formula `odie`s honestly for now)
  - [ ] verify on a second Mac — released and installed here, not yet confirmed
    off the build machine

- [ ] **Studio cleanups** #task
  - [ ] remove the dead opener plugin + 2 capabilities (links use `open_external`)
  - [x] narrow `.gitignore` `studio/.downes/` → `studio/.downes/courses/`; `.gitmodules` re-included (the `.*` rule hid it too)
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
- [ ] **Layer 4 containment — VM or container** #research — RAISED TWICE by
  Alexander (2026-09-01), both times while fighting sandbox fallout: "I really
  really wish these were self contained in a little VM". Treat the repetition
  as signal, not a passing wish
  - [ ] revisit once 0.1.8 is working on teammate machines — his explicit
    sequencing: get it working, then reflect on the VM
  - [ ] ladder already recorded in `docs/decisions/vm-containment.md`: Apple
    `container`, not QEMU or bochs. Deferred on structure, not weight
  - [ ] evidence FOR, gathered this session: the Seatbelt fence is implicated in
    the pane crash loop, denied the npm cache, and the state-isolation seam is
    where several defects landed. A VM would replace that seam with a boundary
  - [ ] evidence AGAINST is still what the decision doc says — it costs the
    whole product again. Bring real numbers to the revisit, not a mood
- [ ] **build.sage.education and the app should point at each other** #task —
  today neither does; nothing shipped mentions the site
  - [ ] site carries the platform, not only describes it (embed mini)
  - [ ] product links out: `caveats` on both casks, README, studio UI
  - [ ] `homepage` in the casks is sage.is/mini; decide which is canonical
  - [ ] blocked until mini is confirmed working on teammate machines
- fog: Sage gateway (api.sage.is), allowlist proxy for host-pinning, corpus
  growth, Obsidian polish, wterm/ghostty engine swap, startr.style in the viewer

## Out of scope

- Multi-model routing — superseded by opencode native model config.
- HyperTalk agent.py readability — superseded; narration in `docs/dossiers/`.
- Intro auto-generation — superseded by native skill discovery.

## Done

- [x] Markdown-First Refactoring — stub at `docs/completed-todos.md`
- [x] SearXNG URL preservation fix — stub at `docs/completed-todos.md`
