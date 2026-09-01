# Team test — v0.1.11 pre-release

This build is verified on ONE Mac only. That machine is where every bug this cycle was found. Your machine is the real test.

~15 minutes. No setup beyond Homebrew.

## Install

```
brew tap sage-is/apps
brew install --cask sage-is/apps/mini
brew install --cask sage-is/apps/downes
```

Apple Silicon only. The cask refuses Intel deliberately — report it, don't work around it.

Workspaces created on first launch: `~/SAGE.ISmini` (mini), `~/Downes` (Downes).

mini's window title reads "SAGE.IS mini". Downes' reads "SAGE.IS".

Uninstall: `brew uninstall --cask mini downes` (keeps courses). Add `--zap` to also remove our state. Neither deletes the user's work.

## Checklist

- [x] Spotlight search "mini" offers SAGE.IS mini — not "Sage.is mini" (screenshot if wrong)
- [x] App launches, title bar correct
- [x] Terminal text renders in Annotation Mono — a distinctive mono face,
      not Menlo. If it looks like the system default, say so
- [x] Terminal pane appears INSIDE the window and accepts typing
- [x] Same for Downes
- [x] In Downes ask for a real lesson/quiz and watch where files land
  - [*] They land either next to courses or in it depending on it they are loose or part of a course
  - [!] Note opencode WEB search doesn't seem to be working on the tester's system
- [x] Downes must write into `courses/` WITHOUT asking permission — being asked is a finding
- [!] Cmd-Q leaves nothing running
  - [!] Looked ok but this was found with pgrep
```
         2294 /opt/homebrew/Cellar/downes/0.1.3/libexec/bin/opencode serve --hostname 127.0.0.1 --port 49345
2328 /opt/homebrew/Cellar/downes/0.1.3/libexec/bin/opencode serve --hostname 127.0.0.1 --port 49610
```

## Known — don't report these

- mini asks before every edit (by design — it has no folder convention to allow-list and no blanket rule is safe; Downes does not ask)
- `mini --version` prints an engine build stamp not 0.1.11
- Kill on the app orphans the engine; Cmd-Q is covered
- No Intel build yet

## What we most want

1. **Does the terminal pane work?** It crash-looped until PWD was traced as the cause. A machine that never had the repo should be clean. A failure means a second cause.

2. **Did you already have opencode installed?** With it the launcher seeds credentials and you land authenticated. Without it you get a login. Both are valid — say which.

3. **Anything reaching outside its workspace?** Neither app should touch `~/Documents`, `~/Desktop` or `~/Downloads`. A macOS prompt for those means stop and screenshot.

## If the pane dies

It now stops after 5 attempts and prints the command it tried. That line is the useful part. Send it verbatim.

## Report

- macOS version and chip
- Whether opencode was already installed
- The checklist
- Screenshots plus the log for failures

Attach the log on failure:

```
tail -40 ~/SAGE.ISmini/.downes/xdg/data/downes/log/opencode.log
```

Check nothing is left after Cmd-Q:

```
pgrep -fl opencode
```

Empty is correct.
