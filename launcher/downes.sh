#!/usr/bin/env bash
# Downes launcher — pins the studio, isolates all opencode state under it,
# and boots the agent. The single source of truth for environment,
# bootstrap, credentials, and (Checkpoint 3) the sandbox prefix.
set -euo pipefail

STUDIO="${DOWNES_STUDIO:-$HOME/Downes}"
DHOME="$STUDIO/.downes"
HERE="$(cd "$(dirname "$0")" && pwd)"

# --- first-launch bootstrap (idempotent, additive) -----------------------
if [ ! -f "$STUDIO/opencode.json" ]; then
  bash "$HERE/../scripts/install_studio.sh" "$STUDIO"
fi
mkdir -p "$DHOME/config/themes" "$DHOME/xdg/data" "$DHOME/xdg/state" "$DHOME/xdg/cache"

# --- isolation -----------------------------------------------------------
# XDG_CONFIG_HOME points the "global" config location at an empty dir the
# studio owns, so the user's ~/.config/opencode (plugins included) never
# loads. The studio config loads via OPENCODE_CONFIG — an explicit config
# whose {file:...} refs resolve against its own location, the studio root.
# Project configs are disabled so a downloaded course cannot smuggle one in.
export XDG_CONFIG_HOME="$DHOME/xdg/config"
export OPENCODE_CONFIG="$STUDIO/opencode.json"
export OPENCODE_PURE=1
export XDG_DATA_HOME="$DHOME/xdg/data"           # own auth.json + opencode.db
export XDG_STATE_HOME="$DHOME/xdg/state"
export XDG_CACHE_HOME="$DHOME/xdg/cache"
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export OPENCODE_DISABLE_AUTOUPDATE=1
export OPENCODE_DISABLE_EXTERNAL_SKILLS=1
export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1

# --- credentials: Sage when present, Zen public floor otherwise ----------
KEY="$(security find-generic-password -s is.sage.downes -w 2>/dev/null || true)"
if [ -n "$KEY" ]; then
  export DOWNES_SAGE_KEY="$KEY"
  export OPENCODE_CONFIG_CONTENT='{"model":"sage/downes-standard"}'
fi

[ -t 1 ] && printf '\033]0;Downes — the studio\007'
cd "$STUDIO"

# Prefer the compiled branded binary (idles near 0% CPU); then the fork run
# from source; then the system opencode.
FORK="$HERE/../ai-ui-mini/packages/opencode"
ARCH="x64"; [ "$(uname -m)" = "arm64" ] && ARCH="arm64"
BIN="$FORK/dist/opencode-darwin-$ARCH/bin/opencode"
if [ -x "$BIN" ]; then
  exec "$BIN" "$@"
fi
if [ -f "$FORK/src/index.ts" ] && [ -d "$FORK/node_modules/@opentui" ]; then
  exec bun run --cwd "$FORK" --conditions=browser src/index.ts "$@"
fi
exec opencode "$@"
