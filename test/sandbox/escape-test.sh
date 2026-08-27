#!/usr/bin/env bash
# Layer-3 escape test. Every deny must deny, every allow must allow, or the
# word "sandboxed" stays off every page. Exit nonzero on any failure.
#
# Two rules this file learned the hard way:
#
#   1. A failing command is not proof of containment. `ls ~/Documents` fails on
#      a clean CI runner because the directory is absent, not because the fence
#      stopped it — every filesystem case would report "ok (denied)" against a
#      profile that fences nothing. So a deny case must see the kernel say
#      "Operation not permitted", and says INCONCLUSIVE when the target is
#      missing rather than banking a false green.
#
#   2. A test that configures the environment itself proves only that the test
#      works. The engine cases run launcher/downes.sh — the shipped entry
#      point — so reverting the isolation or the sandbox prefix turns them red.
set -u

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
STUDIO="${DOWNES_STUDIO:-$HOME/Downes}"

# Physical paths. The macOS sandbox canonicalizes before matching a subpath
# rule, so an unresolved /var/folders/... or /tmp/... never matches its own
# allow and the rule is silently dead. This mirrors launcher/downes.sh.
STUDIO_PHYS="$(cd "$STUDIO" 2>/dev/null && pwd -P || echo "$STUDIO")"
TMP_PHYS="$(cd "${TMPDIR:-/tmp}" 2>/dev/null && pwd -P || echo /private/tmp)"

SB=(sandbox-exec
    -D "STUDIO=$STUDIO_PHYS" -D "TMP=$TMP_PHYS" -D "HOMEDIR=$HOME"
    -f "$REPO/launcher/downes.sb")
F=0
INCONCLUSIVE=0

# The profile names STUDIO as the one writable tree, so it has to exist before
# anything is measured. On a fresh CI runner it does not.
mkdir -p "$STUDIO_PHYS"

# A deny must come from the sandbox. Anything else — a missing file, a typo in
# the command — is reported as inconclusive, never as a pass.
expect_deny() {
  local out
  out="$("${SB[@]}" /bin/sh -c "$1" 2>&1)"
  if [ -z "$out" ] && "${SB[@]}" /bin/sh -c "$1" >/dev/null 2>&1; then
    echo "FAIL (allowed): $2"; F=1; return
  fi
  case "$out" in
    *"Operation not permitted"*|*"Permission denied"*)
      echo "ok (denied):    $2" ;;
    *"No such file"*|*"does not exist"*)
      echo "INCONCLUSIVE:   $2 — target absent, the fence was never tested"
      INCONCLUSIVE=$((INCONCLUSIVE+1)) ;;
    *)
      echo "INCONCLUSIVE:   $2 — failed for another reason: ${out%%$'\n'*}"
      INCONCLUSIVE=$((INCONCLUSIVE+1)) ;;
  esac
}

# Run from the studio, as launcher/downes.sh does with `cd "$STUDIO"`.
# Load-bearing, not tidiness: the profile denies reads under ~/Documents, and a
# checkout that happens to live there poisons anything that reads its own
# working directory — Python's import machinery scans cwd, so `import ctypes`
# fails with EPERM and the case reports a sandbox problem that is not there.
expect_allow() {
  if (cd "$STUDIO_PHYS" && "${SB[@]}" /bin/sh -c "$1" >/dev/null 2>&1); then
    echo "ok (allowed):   $2"
  else
    echo "FAIL (denied):  $2"; F=1
  fi
}

# Network denial does not surface as "Operation not permitted" through curl,
# so it stays exit-code based — and the paired :443 allow above it is what
# shows the fence is live rather than the network being down.
expect_deny_net() {
  if "${SB[@]}" /bin/sh -c "$1" >/dev/null 2>&1; then
    echo "FAIL (allowed): $2"; F=1
  else
    echo "ok (denied):    $2"
  fi
}

# --- filesystem -------------------------------------------------------------
expect_deny  'ls "$HOME/Documents"'                          "read ~/Documents"
# Listed, not globbed: `cat ~/.ssh/id_*` with no matching key leaves the glob
# literal, so the case fails on ENOENT and measures nothing.
expect_deny  'ls "$HOME/.ssh"'                               "read ~/.ssh"
expect_deny  'cat "$HOME/.zsh_history"'                      "read shell history"
expect_deny  'touch "$HOME/Desktop/downes-escape.txt"'       "write ~/Desktop"
expect_deny  "cp -r '$STUDIO_PHYS' \"\$HOME/Documents/exfil\"" "copy studio out"

# Credential stores. The profile allows reads broadly and denies these back, so
# each one is a rule that must actually be present — this is the list a course
# would go looking for, and :443 egress is open.
expect_deny  'cat "$HOME/.local/share/opencode/auth.json"'   "read the shared opencode auth store"
expect_deny  'cat "$HOME/.config/gh/hosts.yml"'              "read GitHub CLI tokens"
expect_deny  'cat "$HOME/.claude.json"'                      "read ~/.claude.json"
expect_deny  'cat "$HOME/.gitconfig"'                        "read ~/.gitconfig"
expect_deny  'ls "$HOME/Library/Application Support"'        "read app support (browser profiles)"

expect_allow "echo hi > '$STUDIO_PHYS/.sandbox-probe' && rm '$STUDIO_PHYS/.sandbox-probe'" "write inside studio"

# The TMP allow is easy to make dead by passing an unresolved path, and nothing
# else in the suite would notice: mktemp, bash heredocs and every compiler need
# it, but `opencode --version` does not touch a temp file.
expect_allow 'f=$(mktemp) && echo hi > "$f" && rm "$f"'      "write inside TMPDIR"
expect_allow 'cat <<EOF
heredoc
EOF'                                                          "bash heredoc (needs a temp file)"

# The studio's terminal pane allocates a pty. `(allow pseudo-tty)` does not
# cover opening /dev/ptmx and the device it hands back, and without those
# openpty() returns "out of pty devices" — surfaced to the teacher as
# "Could not start the Downes terminal: /api/pty → 500".
expect_allow 'python3 -c "import pty; pty.openpty()"'         "allocate a pty (studio terminal)"

# --- network ----------------------------------------------------------------
expect_allow    'curl -sS --max-time 10 https://opencode.ai -o /dev/null' "TLS egress :443"
expect_deny_net 'curl -sS --max-time 5 http://example.com -o /dev/null'   "plain HTTP :80"

# --- the shipped launcher ---------------------------------------------------
# These run launcher/downes.sh itself. Revert the XDG exports or the
# sandbox-exec prefix and they go red — which the previous version of this
# file, which set XDG_* by hand, could not do.
LAUNCHER="$REPO/launcher/downes.sh"
ENGINE=""
for cand in "${DOWNES_ENGINE:-}" \
            "$REPO/bin/opencode" \
            "$REPO/ai-ui-mini/packages/opencode/dist/opencode-darwin-arm64/bin/opencode" \
            "/opt/homebrew/opt/downes/libexec/bin/opencode" \
            "/opt/homebrew/opt/mini/libexec/bin/opencode"
do
  [ -n "$cand" ] && [ -x "$cand" ] && { ENGINE="$cand"; break; }
done

if [ ! -x "$LAUNCHER" ] || [ -z "$ENGINE" ]; then
  echo "INCONCLUSIVE:   launcher cases skipped (no engine built or installed)"
  INCONCLUSIVE=$((INCONCLUSIVE+1))
else
  SCRATCH="$(mktemp -d)"
  trap 'rm -rf "$SCRATCH"' EXIT
  LSTUDIO="$SCRATCH/studio"
  BEFORE="$(ls -1 "$HOME/.local/share/opencode" 2>/dev/null | sort | shasum | cut -d' ' -f1)"

  if DOWNES_STUDIO="$LSTUDIO" DOWNES_ENGINE="$ENGINE" "$LAUNCHER" --version >/dev/null 2>&1; then
    echo "ok (allowed):   launcher starts the engine"
  else
    echo "FAIL (denied):  launcher starts the engine"; F=1
  fi

  # The launcher exported XDG_* into the studio, so the engine built its store
  # there rather than in the home directory.
  # data/downes, not data/opencode: the fork names its XDG folder after itself
  # (core/src/global.ts) so it can never share a directory with a stock
  # opencode install. A regression there would show up here as this case going
  # red rather than as someone else's corrupted database.
  if [ -d "$LSTUDIO/.downes/xdg/data/downes" ]; then
    echo "ok (allowed):   launcher put engine state inside the studio"
  else
    echo "FAIL (denied):  launcher put engine state inside the studio"; F=1
  fi

  AFTER="$(ls -1 "$HOME/.local/share/opencode" 2>/dev/null | sort | shasum | cut -d' ' -f1)"
  if [ "$BEFORE" = "$AFTER" ]; then
    echo "ok (denied):    launcher left the shared home store untouched"
  else
    echo "FAIL (allowed): launcher wrote to the shared home store"; F=1
  fi

  # The env fix holds only where the env is set. This case removes it entirely
  # and asserts the BINARY still stays out of a stock opencode's directory —
  # the property that makes the collision structurally impossible rather than
  # merely absent. A colleague lost a morning to this exact failure.
  NAKED="$(mktemp -d)"
  ( cd "$NAKED" && env -u XDG_CONFIG_HOME -u XDG_DATA_HOME -u XDG_STATE_HOME \
      -u XDG_CACHE_HOME HOME="$NAKED" "$ENGINE" --version >/dev/null 2>&1 )
  if [ -d "$NAKED/.local/share/opencode" ]; then
    echo "FAIL (allowed): unisolated engine wrote into ~/.local/share/opencode"; F=1
  else
    echo "ok (denied):    unisolated engine stays out of the opencode store"
  fi
  rm -rf "$NAKED"

  # The launcher must actually apply the fence, not merely be capable of it.
  if DOWNES_STUDIO="$LSTUDIO" DOWNES_ENGINE=/bin/sh "$LAUNCHER" \
       -c 'touch "$HOME/Desktop/downes-escape-probe"' >/dev/null 2>&1; then
    echo "FAIL (allowed): launcher applies the sandbox prefix"; F=1
    rm -f "$HOME/Desktop/downes-escape-probe"
  else
    echo "ok (denied):    launcher applies the sandbox prefix"
  fi

  # The cask links brew's bin/downes at the launcher INSIDE the app bundle.
  # Deriving paths from the link's directory instead of the target's makes the
  # payload lookup land in /opt/homebrew/bin, where ../bin/opencode is a stock
  # opencode — our command silently ran their engine and reported their version.
  SHIM="$SCRATCH/bin"; mkdir -p "$SHIM"
  ln -sf "$LAUNCHER" "$SHIM/downes"
  if DOWNES_STUDIO="$LSTUDIO" DOWNES_ENGINE="$ENGINE" DOWNES_NO_SANDBOX=1 \
       "$SHIM/downes" --version 2>/dev/null | grep -q downes; then
    echo "ok (allowed):   launcher resolves itself through a symlink"
  else
    echo "FAIL (denied):  launcher resolves itself through a symlink"; F=1
  fi

  # And the documented bypass must still work, or debugging is impossible.
  if DOWNES_STUDIO="$LSTUDIO" DOWNES_ENGINE=/usr/bin/true DOWNES_NO_SANDBOX=1 \
       "$LAUNCHER" >/dev/null 2>&1; then
    echo "ok (allowed):   DOWNES_NO_SANDBOX=1 bypasses the fence"
  else
    echo "FAIL (denied):  DOWNES_NO_SANDBOX=1 bypasses the fence"; F=1
  fi

  # The studio runs `opencode serve`, which binds a loopback port. The profile
  # had no network-bind rule for a long time and nothing noticed, because every
  # engine case here ran `--version` — which never binds. Serving under the
  # fence is the assertion that covers the GUI's actual code path.
  SPORT=51987
  SLOG="$SCRATCH/serve.log"
  ( cd "$STUDIO_PHYS" && \
    env XDG_CONFIG_HOME="$LSTUDIO/.downes/xdg/config" \
        XDG_DATA_HOME="$LSTUDIO/.downes/xdg/data" \
        XDG_STATE_HOME="$LSTUDIO/.downes/xdg/state" \
        XDG_CACHE_HOME="$LSTUDIO/.downes/xdg/cache" \
        "${SB[@]}" "$ENGINE" serve --hostname 127.0.0.1 --port "$SPORT" \
        >"$SLOG" 2>&1 ) &
  SPID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    grep -q "listening" "$SLOG" 2>/dev/null && break
    sleep 1
  done
  if [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 \
          "http://127.0.0.1:$SPORT/api/health" 2>/dev/null)" != "000" ]; then
    echo "ok (allowed):   engine binds a loopback port under the fence"
  else
    echo "FAIL (denied):  engine binds a loopback port under the fence"
    F=1
    [ -s "$SLOG" ] && sed 's/^/                  /' "$SLOG" | head -3
  fi
  kill "$SPID" 2>/dev/null
  wait "$SPID" 2>/dev/null

  # Sharing state while fenced cannot work, so the launcher must refuse it
  # rather than hand the user an engine that cannot open its own log.
  if DOWNES_STUDIO="$LSTUDIO" DOWNES_ENGINE=/usr/bin/true DOWNES_SHARE_STATE=1 \
       "$LAUNCHER" >/dev/null 2>&1; then
    echo "FAIL (allowed): DOWNES_SHARE_STATE=1 refused while fenced"; F=1
  else
    echo "ok (denied):    DOWNES_SHARE_STATE=1 refused while fenced"
  fi
fi

if [ "$INCONCLUSIVE" != 0 ]; then
  echo "escape test: $INCONCLUSIVE case(s) INCONCLUSIVE — coverage is smaller than it looks"
fi
[ "$F" = 0 ] && echo "escape test: ALL GREEN" || echo "escape test: FAILURES"
exit $F
