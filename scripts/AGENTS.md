# scripts/AGENTS.md

Briefing for anyone — human or agent — touching `scripts/` in this repo. Read
this before changing `package_macos.sh` or `package_windows.ps1`.

## What builds what

| Script | Platform | Output | Products |
|---|---|---|---|
| `package_macos.sh [arm64\|x64] [downes\|mini]` | macOS (darwin) | `.tar.gz` + `.dmg`, both sha256'd | `downes` or `mini` |
| `package_windows.ps1 -Product <downes\|mini> -Arch <x64\|arm64>` | Windows | NSIS `-setup.exe`, sha256'd | `downes` or `mini` |

Both scripts share one Rust shell binary (`ai-ui-mini/packages/studio`) and
one Bun-compiled engine (`ai-ui-mini/packages/opencode`). They differ only in
bundle metadata and payload contents:

- `downes` — the curriculum agent. Ships the studio template (skills, METHOD,
  prompts) from `studio/` in this repo. AGPL content.
- `mini` — the bare Sage.is AI-UI mini platform. No curriculum, no template.
  MIT only.

macOS cannot cross-build for Windows and vice versa: each script bundles the
engine built for its own host.

## Invariants — do not break these

Every one of these exists because it broke in a real release. If your change
touches the areas below, keep the guard, don't weaken it.

- **Channel pin** (`OPENCODE_CHANNEL=downes/v1`). Left unset, the fork falls
  back to the current git branch name, and that name becomes the database
  filename. A release cut from the wrong branch ships a different database
  path than the last one. Pin it explicitly in both scripts.
- **Version stamp** (`OPENCODE_VERSION`, from `engine-version.ts`). Left
  unset, the build stamps `0.0.0-<channel>-<timestamp>`. `0.0.0` fails every
  provider gate that checks a minimum opencode version — providers do check.
  One derivation (`engine-version.ts`, reads `packages/opencode/package.json`)
  feeds both platforms so a Windows build reports the same number as macOS.
- **Engine freshness and version assertions.** `package_macos.sh` rebuilds the
  engine when it is missing, when any engine source is newer than it, or when
  it reports a version other than `OPENCODE_VERSION`. `package_windows.ps1`
  checks the reported version only; `stage-payload.ts` checks it again before
  staging. Both then assert after building. Stale engines shipped twice: every
  macOS release from v0.1.3 to v0.1.12 carried the engine built on 27 August,
  and a Windows 0.1.13 installer carried one twelve days old, still reporting
  `0.0.0-downes/v1-<timestamp>`. Do not skip the post-build assertion to save
  time.
- **Self-containment.** An installed copy has no source checkout above it —
  it resolves its engine relative to its own executable path, never a fork
  checkout. `package_macos.sh` proves this by grepping the staged payload
  and the studio binary for `Documents/Projects/GitHub` and failing if found.
  `stage-payload.ts` is the only thing that puts an engine into a Windows
  bundle; there's no Homebrew cask on Windows to backfill it afterward.
- **Product marker** (`payload/product`, or `Contents/Resources/product` on
  macOS). One binary serves both products; this file is how it decides which
  workspace folder it owns. On Windows it's the *only* channel — the
  fallback path parses `Info.plist`, which no Windows bundle has, so an
  unmarked mini bundle would name its window correctly and still write into
  `~/Downes`.
- **Codesign then quarantine handling, macOS only.** Sign the engine first,
  verify it, then sign and verify the whole `.app` — in that order. The
  engine is a Bun single-file executable that appends its payload after
  signing, so a bundle sealed around an unsigned/broken engine doesn't just
  warn on launch, it hangs on exec under quarantine. `--deep` does not catch
  this: it descends into nested bundles/frameworks, not loose Mach-O files
  under `Resources`.

## Licence boundary

The curriculum template (`studio/` in this repo) is AGPL. `ai-ui-mini` is MIT
and must never carry a copy of it in its history. A Windows `downes` build does
copy it into `packages/studio/src-tauri/payload/studio`, which is gitignored
and wiped at the start of every staging run; keep it that way, and never commit
it.

`stage-payload.ts` enforces this by only copying what `DOWNES_TEMPLATE`
points at. `package_windows.ps1` sets `DOWNES_TEMPLATE` for `downes` builds
and unsets it for `mini`. If `DOWNES_TEMPLATE` is unset, `stage-payload.ts`
stages no template at all — the running app then writes a default
`opencode.json` and treats itself as the bare platform. Never point
`DOWNES_TEMPLATE` at anything for a `mini` build, and never add a fallback
that copies the template by default.

## Deliberately not done

- **No notarization** on macOS. Signing here is ad hoc (`codesign --sign -`),
  not Developer ID. Gatekeeper will still flag a fresh download.
- **No Windows code signing.** The installer is unsigned; SmartScreen warns
  on first run — "More info", then "Run anyway". Don't imply otherwise in
  release notes.
- **No containment on Windows.** macOS runs the engine under a Seatbelt
  profile (`launcher/downes.sb`, staged into the app). Windows has no
  counterpart. Say the Windows app "works in one folder" — never call it
  sandboxed.

## Running them

**macOS**, from the repo root:
```
scripts/package_macos.sh [arm64|x64] [downes|mini]
```
Defaults to the host arch and `downes`. Check the printed sha256 lines at the
end; both `.tar.gz` and `.dmg` are written to `dist/`. If the engine or app
bundle rebuild triggers, read the `==> building ... (<reason>)` line — it
names which invariant tripped.

**Windows**, from a Windows machine with bun, the MSVC Rust toolchain, and
WebView2 installed:
```
scripts/package_windows.ps1 -Product downes -Arch x64
```
Output lands in `dist\<product>-<version>-windows-<arch>-setup.exe`. The
script itself asserts the payload contains `bin\opencode.exe`, `product`,
and — for `downes` — `studio\opencode.json` before it finishes; a thrown
error there means the payload is incomplete, not that the build failed.

After either script: confirm the version in the output filename matches
`ai-ui-mini/packages/studio/src-tauri/tauri.conf.json`, and that the sha256
printed matches the file on disk before you publish it.
