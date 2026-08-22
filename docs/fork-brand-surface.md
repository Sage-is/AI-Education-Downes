# Fork brand surface — ai-ui-mini

The fork of `anomalyco/opencode` @ `v1.18.18`, living in the separate MIT
repo `ai-ui-mini`. The whole brand change is one new file plus ~8 one-to-
three-line import patches, kept as a `git format-patch` series so a rebase
onto the next upstream tag is a ≤20-minute afternoon.

## The one new file

`packages/core/src/brand.ts` — the single source of truth:

```ts
export const BRAND = {
  platformName: "Sage.is AI-UI mini",
  agentName: "Downes",
  binName: "downes",
  tuiWordmark: /* Downes ASCII art */,
  cliWordmark: /* CLI help ASCII art */,
  splashLine: "Downes — the studio",
  footerCredit: "Sage.is AI-UI mini · Powered by Sage.is and OpenCode",
}
```

## The patch points (VERIFIED by cloning + running v1.18.18)

Applied and committed on branch `downes/v1` (fork commit 3022d91):

| File | Change | Status |
|------|--------|--------|
| `packages/tui/src/logo.ts` | `opencode` wordmark → `downes` block art, two-tone dow/nes | DONE |
| `packages/tui/src/routes/home.tsx` | placeholder examples (`Fix a TODO in the codebase`) → course-design prompts | DONE |
| `packages/tui/src/feature-plugins/home/tips-view.tsx` | `NO_MODELS_TIP` (`/connect … start coding`) → "ask Downes to design a course" | DONE |

Still to do for the full brand pass (lower visibility):

| File | Change |
|------|--------|
| `packages/opencode/package.json` | `bin` `opencode` → `downes` (compiled-install only) |
| the remaining `/connect` tips in `tips-view.tsx` | curriculum wording or removal |
| `packages/opencode/src/cli/logo.ts` | re-exports `@opencode-ai/tui/logo` — inherits the new wordmark automatically |
| footer provider label "OpenCode Zen" | keep — it is the nominative "Powered by OpenCode" credit |

`brand.ts` was NOT needed as a separate constants file for v1 — the changes
are small and local. Introduce it only if the surface grows.

## Running the fork (verified)

No compile needed for a branded preview: the launcher runs the fork from
source via `bun run --cwd <fork>/packages/opencode --conditions=browser
src/index.ts`. Requires `bun install` in the fork (bun's isolated layout
puts `@opentui` under each package's `node_modules`; the
`tree-sitter-powershell` postinstall fails on a missing `node-gyp` but is an
optional grammar — harmless). A compiled `downes` binary
(`bun run build`) is the shipping step, deferred.

## Discipline

- `LICENSE` stays byte-identical — never touched.
- Do NOT reopen upstream issue #12016 (custom logo config, closed).
- Brand assets (wordmark, splash, theme palette `downes.json`) drafted by
  us, approved before the series is cut.
- Rebase drill: `git rebase --onto <newtag> v1.18.18 downes/v1 && bun install
  && bun run typecheck`; time it; target ≤20 min; monthly.
- GUI surfaces (the v2 Tauri wrapper, web exports) style with startr.style
  (mobile-first) and startr.swap; the TUI keeps its theme palette.
