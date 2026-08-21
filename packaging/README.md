# Packaging

Two install paths for v1. Apple notarization is backlogged (see TODO.md).

## Homebrew tap (primary)

```bash
brew install sage-is/tap/downes
downes
```

The tap delivers the `ai-ui-mini` fork binary, the launcher, and
`Downes.app`. Tap installs are not quarantined by Gatekeeper, so the app
runs with zero code signing. Formula: `homebrew/downes.rb`, published to the
`Sage-is/homebrew-tap` repo.

## Unsigned DMG (for the brave)

A drag-to-Applications DMG ships alongside for teachers without Homebrew.
Because it is unsigned, first launch requires **right-click → Open** to pass
the Gatekeeper warning — documented on the download page. The signed,
notarized DMG is the backlog item that removes this step.

## Updates

`brew upgrade downes`, plus the launcher checking a static version JSON on
sage.is. `autoupdate` stays `notify`/`false` — Downes never self-updates
from upstream opencode.
