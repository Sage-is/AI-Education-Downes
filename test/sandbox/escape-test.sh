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

[ "$F" = 0 ] && echo "escape test: ALL GREEN" || echo "escape test: FAILURES"
exit $F
