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

**Apple Silicon only for now** — an Intel build needs a CI runner. Formula: `homebrew/downes.rb`, published to the
`Sage-is/homebrew-apps` repo (tap slug `sage-is/apps`).

## Unsigned DMG (for the brave)

A drag-to-Applications DMG ships alongside for teachers without Homebrew.
Because it is unsigned, first launch requires **right-click → Open** to pass
the Gatekeeper warning — documented on the download page. The signed,
notarized DMG is the backlog item that removes this step.

## Updates

`brew upgrade downes`, plus the launcher checking a static version JSON on
sage.is. `autoupdate` stays `notify`/`false` — Downes never self-updates
from upstream opencode.
