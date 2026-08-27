# Decision: virtual machines and emulators for containment

Status: **RECOMMENDED — pending advisor ratification.** Raised by a dev
proposing QEMU or bochs; this records the whole ladder so the question does not
have to be re-derived.

## Recommendation

Ship **no VM or emulator in v1.** Containment is the macOS Seatbelt profile
(`launcher/downes.sb`), wired on both surfaces — `launcher/downes.sh` for the
terminal and `sandbox_prefix()` in
`ai-ui-mini/packages/studio/src-tauri/src/lib.rs` for the studio sidecar — and
guarded by `make sandbox_test`. When Layer 4 is needed, it is **Apple
`container`** — not QEMU, and not bochs.

## Why

The v1 threat is a downloaded course reading or exfiltrating the teacher's
files. A syscall fence answers that at zero install cost. A VM answers it too,
and costs the whole product again.

**The VM tier is deferred on structure, not weight.** Every rung below the line
runs a Linux guest, and our engine is a macOS ARM64 Bun single-file executable.
Each costs the same three things:

1. A second engine build for `linux-arm64`.
2. A guest root filesystem in the payload — against 150 MB today.
3. `virtiofs`-style sharing to give the guest the studio folder.

Sub-second boot removes the wait, not the work. That is the honest reason to
defer, and a better one than "QEMU is big".

**A VM would not have solved the problem we actually had.** What kept the
sandbox unwired was state layout: every product resolved `XDG_*` to the same
`~/.local/share/opencode`. A guest with the user's home shared in reproduces
that collision inside the VM. Fixing the layout was the prerequisite either way.

### The ladder

Lightest first. Above the line is free; below the line costs a Linux guest.

| Rung | Weight | Runs on | Verdict |
|---|---|---|---|
| Env/state isolation (`XDG_*`) | zero | all | **Shipped.** Prerequisite for everything below |
| Engine permission config | zero | all | In use; not OS-enforced — a third-party TUI ignores it |
| Seatbelt (`sandbox-exec`) | in-box | macOS | **Shipped.** Deprecated by Apple, working on 26.5.1, no removal date |
| Landlock | in-kernel 5.13+ | Linux | The light Linux answer; beats bubblewrap — unprivileged, no setuid helper, inherited across `exec` |
| Separate low-privilege user | zero deps | all three | Light and portable. **Rejected on UX** — user switching wrecks Finder, Keychain and drag-drop |
| AppContainer / LPAC | weeks of Win32 | Windows | Deferred; see `windows-sandbox.md` |
| **Apple `container`** | Apache-2.0, sub-second boot | macOS 26+, Apple Silicon | **The chosen Layer 4.** v1.0.0, 2026-06-09. Licence fits mini's MIT |
| libkrun / krunkit | VMM inside the host process | macOS ARM, Linux KVM | Lighter still. Same Linux-guest cost |
| Firecracker | ~125 ms boot | Linux + KVM only | Not our shipping platform |
| QEMU | ~500 MB + 15 deps + guest image | most | `GPL-2.0-only` against mini's MIT; HVF needs `com.apple.security.hypervisor` + codesign |
| Bochs | ~100 MIPS ceiling, interpreted | all | **Disqualified** — x86 guests only; would emulate an Intel PC on Apple Silicon |

## When Layer 4 becomes necessary

**Multi-harness.** A syscall fence cannot contain a harness we did not write.
pi and deepseek-harness would run as our children with our permissions;
`downes.sb` constrains the filesystem but not what a third-party binary does
inside it, and the engine's own permission config is advisory to anything that
does not read it. That is the case Apple `container` answers.

The migration is contained rather than a rewrite: the studio already talks to
the sidecar over authenticated HTTP
(`ai-ui-mini/packages/studio/frontend/src/api.ts`), so the sidecar can move
into a micro-VM behind the same interface.

## Guardrail

No page says "virtual machine", "VM-isolated" or "hardware isolation" until a
guest actually ships and passes an escape test.

The honest claim is what `downes.sb` actually enforces, which is asymmetric:

- **Writes** are deny-default — the studio, `TMPDIR`, and `/private/tmp`
  (bash puts here-document temp files there and ignores `TMPDIR`).
- **Reads** are the opposite: a blanket `file-read*` allow with an enumerated
  deny-list back. Anything not on that list stays readable. "The filesystem is
  fenced to the studio" is true of writes and false of reads, so do not say it
  unqualified.
- **Egress** is TLS-only, plus loopback bind and inbound for the studio's own
  sidecar. SBPL cannot pin hostnames, so "TLS-only egress" is the ceiling of
  that claim, not "we control where it connects" — and because reads are a
  deny-list, whatever remains readable is also exfiltratable.

Re-open when multi-harness is scheduled, or if Apple removes `sandbox-exec` —
[apple/containerization#737](https://github.com/apple/containerization/issues/737),
open, no removal timeline.
