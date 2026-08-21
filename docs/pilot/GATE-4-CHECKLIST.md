# Gate 4 — ship / no-ship checklist

Each line maps to a Definition-of-Done clause. All must be green to ship.

## Product

- [ ] Unaided install-to-first-output within a reasonable session — teacher
      never needed a path, a picker, or a terminal command beyond `downes`.
- [ ] Real-task `99_summary.md` rated usable as-is or minor-edits by the
      teacher (not major rework).
- [ ] Obsidian open test passed — course reads as one navigable folder.
- [ ] Artifact export test passed — shareable with no extra tooling.
- [ ] First run felt like one safe folder, not a developer terminal.

## Safety

- [ ] "Sandboxed" claim honest: `test/sandbox/escape-test.sh` ALL GREEN on
      the pilot machine's OS, or the copy says "works in one folder".
- [ ] No path strings, no folder picker anywhere in the pilot UI.

## Engineering

- [ ] Nightly replay green on the pinned model within 24 h.
- [ ] `make ci` green (offline gate + one-line test + replay).
- [ ] Fork diff scoped to the brand surface; LICENSE byte-identical.

## Legal / governance

- [ ] Skill licence card resolved (AGPL vs dual).
- [ ] Windows sandbox card resolved, or the pilot explicitly scoped to
      macOS and recorded.
- [ ] Legal matrix has no RED.
- [ ] Advisor sign-off.

## On ship

- [ ] Record `docs/decisions/gate-4-ship.md`.
- [ ] `make minor_release` → v1.0.0.
