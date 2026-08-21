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

## The patch points (verified against v1.18.18 via the GitHub tree)

| File | Change |
|------|--------|
| `packages/tui/src/logo.ts` | import `BRAND.tuiWordmark` |
| `packages/tui/src/component/startup-loading.tsx` | splash → `BRAND.splashLine` |
| `packages/tui/src/feature-plugins/home/footer.tsx` | add `BRAND.footerCredit`; drop the cwd path render |
| `packages/tui/src/routes/session/footer.tsx` | footer credit |
| `packages/tui/src/feature-plugins/sidebar/footer.tsx` | footer credit |
| `packages/opencode/src/cli/logo.ts` | `BRAND.cliWordmark` |
| `packages/opencode/src/cli/ui.ts` | product name string |
| `packages/opencode/src/cli/cmd/run/splash.ts` | `BRAND.splashLine` |
| `packages/opencode/package.json` | `bin` → `downes` |

## Discipline

- `LICENSE` stays byte-identical — never touched.
- Do NOT reopen upstream issue #12016 (custom logo config, closed).
- Brand assets (wordmark, splash, theme palette `downes.json`) drafted by
  us, approved before the series is cut.
- Rebase drill: `git rebase --onto <newtag> v1.18.18 downes/v1 && bun install
  && bun run typecheck`; time it; target ≤20 min; monthly.
- GUI surfaces (the v2 Tauri wrapper, web exports) style with startr.style
  (mobile-first) and startr.swap; the TUI keeps its theme palette.
