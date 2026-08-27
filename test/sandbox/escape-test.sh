#!/usr/bin/env bash
# Layer-3 escape test. Every deny must deny, every allow must allow, or the
# word "sandboxed" stays off every page. Exit nonzero on any failure.
set -u

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
STUDIO="${DOWNES_STUDIO:-$HOME/Downes}"
SB=(sandbox-exec
    -D "STUDIO=$STUDIO" -D "TMP=${TMPDIR%/}" -D "HOMEDIR=$HOME"
    -f "$REPO/launcher/downes.sb")
F=0

# The profile names STUDIO as the one writable tree, so it has to exist before
# anything is measured. On a fresh CI runner it does not.
mkdir -p "$STUDIO"

expect_deny() {
  if "${SB[@]}" /bin/sh -c "$1" >/dev/null 2>&1; then
    echo "FAIL (allowed): $2"; F=1
  else
    echo "ok (denied):    $2"
  fi
}
expect_allow() {
  if "${SB[@]}" /bin/sh -c "$1" >/dev/null 2>&1; then
    echo "ok (allowed):   $2"
  else
    echo "FAIL (denied):  $2"; F=1
  fi
}

expect_deny  'ls "$HOME/Documents"'                          "read ~/Documents"
expect_deny  'cat "$HOME/.ssh/id_"* '                        "read ~/.ssh keys"
expect_deny  'cat "$HOME/.zsh_history"'                      "read shell history"
expect_deny  'touch "$HOME/Desktop/downes-escape.txt"'       "write ~/Desktop"
expect_deny  "cp -r '$STUDIO' \"\$HOME/Documents/exfil\""    "copy studio out"
expect_allow "echo hi > '$STUDIO/.sandbox-probe' && rm '$STUDIO/.sandbox-probe'" "write inside studio"
expect_allow 'curl -sS --max-time 10 https://opencode.ai -o /dev/null' "TLS egress :443"
expect_deny  'curl -sS --max-time 5 http://example.com -o /dev/null'   "plain HTTP :80"

# --- engine-level cases ----------------------------------------------------
# Everything above exercises /bin/sh. Those cases stayed green while the real
# product could not launch under the profile at all: the engine kept its
# auth.json and database in ~/.local/share/opencode, outside the fence. A
# sandbox test that never runs the sandboxed program proves very little.

ENGINE=""
for cand in "${DOWNES_ENGINE:-}" \
            "$REPO/bin/opencode" \
            "$REPO/ai-ui-mini/packages/opencode/dist/opencode-darwin-arm64/bin/opencode" \
            "/opt/homebrew/opt/downes/libexec/bin/opencode" \
            "/opt/homebrew/opt/mini/libexec/bin/opencode"
do
  [ -n "$cand" ] && [ -x "$cand" ] && { ENGINE="$cand"; break; }
done

if [ -z "$ENGINE" ]; then
  echo "SKIP (no engine):  build one or brew install to cover the engine cases"
else
  XDG="$STUDIO/.downes/xdg"
  mkdir -p "$XDG/config" "$XDG/data" "$XDG/state" "$XDG/cache"

  # Run from the studio, exactly as launcher/downes.sh does with `cd "$STUDIO"`.
  # This is load-bearing, not tidiness: the profile denies reads under
  # ~/Documents, and the engine reads its own working directory at startup. Run
  # these cases from a checkout that happens to live in ~/Documents and they
  # fail on the cwd, not on anything the test means to measure.
  engine() {
    (cd "$STUDIO" && env XDG_CONFIG_HOME="$XDG/config" XDG_DATA_HOME="$XDG/data" \
       XDG_STATE_HOME="$XDG/state" XDG_CACHE_HOME="$XDG/cache" \
       "$@" >/dev/null 2>&1)
  }

  # With state isolated into the studio, the engine starts under the fence.
  if engine "${SB[@]}" "$ENGINE" --version; then
    echo "ok (allowed):   engine starts under the profile"
  else
    echo "FAIL (denied):  engine starts under the profile"; F=1
  fi

  # The engine created its store inside the studio, not in the home dir.
  if [ -d "$XDG/data/opencode" ]; then
    echo "ok (allowed):   engine state landed inside the studio"
  else
    echo "FAIL (denied):  engine state landed inside the studio"; F=1
  fi

  # The coupling, stated as an invariant: the shared home store is not
  # writable through the fence. This is why state isolation had to land first
  # — with XDG left alone the engine keeps auth.json and its database here,
  # and switching the sandbox on takes its credentials away on first launch.
  #
  # Probed as a direct write, not by running the engine: ~/.local/share/opencode
  # usually already exists, so the engine's recursive mkdir succeeds without
  # needing write permission and proves nothing.
  expect_deny "touch \"\$HOME/.local/share/opencode/downes-fence-probe\"" \
              "write the shared home store"
fi

[ "$F" = 0 ] && echo "escape test: ALL GREEN" || echo "escape test: FAILURES"
exit $F
