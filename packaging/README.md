# Packaging

Two install paths for v1. Apple notarization is backlogged (see TODO.md).

## Homebrew tap (primary)

```bash
brew install sage-is/apps/downes
downes
```

The tap delivers a self-contained payload: the compiled engine, the
launcher, and `Downes.app`. The engine is a Bun single-file executable, so a
Mac with nothing but Homebrew can run it — no bun, node, or opencode install.

This is a **formula, not a cask**, and deliberately so: casks apply Gatekeeper
quarantine by default, formulas do not. That is what makes this install
warning-free while the app is still unsigned.

That choice has since become the only one available. Homebrew ends support for
casks failing Gatekeeper checks on **2026-09-01** and is deprecating
`--no-quarantine` ([Homebrew/brew#20755](https://github.com/Homebrew/brew/issues/20755)).
The issue scopes the change to casks and does not mention formulas — read that
as inference from silence, not a guarantee, and re-check before leaning on it
in shipped copy. Either way it makes notarization more urgent, not less.

Running `downes` once from a terminal also places the app in `~/Applications`.
The formula cannot: Homebrew replaces `HOME` with a temp directory during
`post_install` and sandboxes it to the formula prefix, so a symlink there
reports success and creates nothing. `launcher/downes.sh` does it instead.

**Apple Silicon only for now** — an Intel build needs a CI runner. Formula: `homebrew/downes.rb`, published to the
`Sage-is/homebrew-apps` repo (tap slug `sage-is/apps`).

## Unsigned DMG (for the brave)

A drag-to-Applications DMG ships alongside for teachers without Homebrew.
Anything downloaded from GitHub *is* quarantined, so first launch requires
**right-click → Open**, or on macOS 26 the **System Settings → Privacy &
Security → "Open Anyway"** route most people actually find.

From a terminal, the same thing:

```bash
xattr -d -r com.apple.quarantine "/Applications/Downes.app"
```

`-r` is required — the attribute sits on files throughout the bundle, not just
the top directory.

This applies to the DMG path only. Homebrew installs are never quarantined, so
do not put this command in the formula caveats: handing a Gatekeeper bypass to
people who are not blocked teaches the wrong reflex. The signed, notarized DMG
is the backlog item that removes the step entirely.

## Updates

`brew upgrade downes`, plus the launcher checking a static version JSON on
sage.is. `autoupdate` stays `notify`/`false` — Downes never self-updates
from upstream opencode.
