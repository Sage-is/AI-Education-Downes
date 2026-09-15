# Packaging

Two install paths for v1 on macOS, plus a Windows installer. Apple
notarization is backlogged (see TODO.md).

## Homebrew tap (primary)

```bash
brew install --cask sage-is/apps/downes    # the curriculum agent
brew install --cask sage-is/apps/mini      # the bare platform
```

The tap delivers a self-contained payload: the compiled engine, the launcher,
and the `.app`. The engine is a Bun single-file executable, so a Mac with
nothing but Homebrew can run it — no bun, node, or opencode install.

**These are casks.** They were formulae through 0.1.3 and became casks at 0.1.4,
which is when Homebrew ended support for casks failing Gatekeeper checks and
deprecated `--no-quarantine`
([Homebrew/brew#20755](https://github.com/Homebrew/brew/issues/20755)).

A cask install *is* quarantined, and the app is ad-hoc signed rather than
notarized, so Gatekeeper would refuse it and the teacher would have to
right-click → Open. Both casks clear the flag themselves in a `postflight`
block. That is a deliberate trade, not an oversight: it disables Gatekeeper's
check for this app on every install, which is precisely the behaviour Homebrew
deprecated `--no-quarantine` to discourage. Notarization is the real fix and
removes the block entirely.

The cask places the app and the command: the `app` stanza moves the bundle into
the Applications folder, and the `binary` stanza links the launcher onto `PATH`.
Nothing needs running first, and no code links the bundle by hand any more.

**Apple Silicon only for now** — an Intel build needs a CI runner, and
`depends_on arch: :arm64` refuses the install rather than half-working. Casks:
`homebrew/downes.rb` and `homebrew/mini.rb`, published to the
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

Do not put that command in the caveats a user reads. The casks already run it in
`postflight`, where it applies to the one app being installed; printing it as
advice teaches a general Gatekeeper bypass to people who are not blocked. The
signed, notarized DMG is the backlog item that removes the step entirely.

## Windows installer

```bash
scripts/package_windows.sh    # from Git Bash, on Windows
```

Writes `dist/downes-<version>-windows-<arch>-setup.exe`, a per-user NSIS
installer. It needs the MSVC Rust toolchain, bun, and the WebView2 runtime.

The fork can build mini for Windows on its own. Downes is that shell plus the
curriculum template, which is AGPL and stays out of the MIT fork, so this
script stages the template and hands it to the fork's `tauri build` as extra
bundle resources. That is what makes the app open on the Downes agent: without
the template the shell writes mini's bare config and opencode falls back to
Build.

Unsigned, so SmartScreen warns on first run. The installer's side and header
art is still mini's; the fork's `make-installer-art.py` draws only that mark.
There is no containment on Windows (`docs/decisions/windows-sandbox.md`).

## Updates

`brew upgrade --cask downes` and `brew upgrade --cask mini`, plus the launcher
checking a static version JSON on sage.is. `autoupdate` stays `notify`/`false` —
Downes never self-updates from upstream opencode.
