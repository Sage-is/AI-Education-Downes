# Decision: Windows containment for v1

Status: **RECOMMENDED — pending advisor ratification** (TODO.md #research card)

## Recommendation

Ship **no OS-level containment on Windows for v1.** Windows Downes uses the
same app-managed studio folder, and the copy says "works in one folder" —
never "sandboxed" — on Windows. Exportable course artifacts are the
cross-platform safety story there.

## Why

- The three real options each cost more than v1 can spend:
  - **AppContainer / LPAC** — the strongest, but weeks of Win32 work and it
    breaks the child tools opencode spawns (ripgrep, LSPs).
  - **Restricted token + job object** — cheaper, but materially leakier;
    read access is hard to fence.
  - **WSL2 + bubblewrap** — real containment, unacceptable install burden
    for a teacher.
- macOS ships the honest sandbox (`launcher/downes.sb`, escape test green).
  Linux has the bubblewrap sketch. Windows containment is a v2 investment
  gated on real Windows demand, not a launch blocker.

## Guardrail

The word "sandboxed" appears in Windows copy only if AppContainer later
lands and passes an escape test. Until then, Windows says "works in one
folder", same honesty bar as the pre-Layer-3 macOS wording.
