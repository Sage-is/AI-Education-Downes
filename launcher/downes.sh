#!/usr/bin/env bash
# Downes launcher — pins the studio, isolates all opencode state under it,
# and boots the agent. The single source of truth for environment,
# bootstrap, credentials, and (Checkpoint 3) the sandbox prefix.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# Which product this payload is. Downes ships the curriculum template; the
# bare Sage.is mini platform does not, and uses its own workspace folder.
# Absent marker means Downes, so existing installs are unaffected.
WORKSPACE="Downes"
[ -f "$HERE/../product" ] && WORKSPACE="$(tr -d '[:space:]' < "$HERE/../product")"

STUDIO="${DOWNES_STUDIO:-$HOME/$WORKSPACE}"
DHOME="$STUDIO/.downes"

# --- first-launch bootstrap (idempotent, additive) -----------------------
# Only when a curriculum template is actually present. mini ships none, and
# install_studio.sh would exit non-zero copying a template that is not there,
# taking the whole launcher down with it under `set -e`.
if [ ! -f "$STUDIO/opencode.json" ] && [ -f "$HERE/../studio/opencode.json" ]; then
  bash "$HERE/../scripts/install_studio.sh" "$STUDIO"
fi
mkdir -p "$STUDIO"
mkdir -p "$DHOME/config/themes" "$DHOME/xdg/data" "$DHOME/xdg/state" "$DHOME/xdg/cache"

# --- config layer --------------------------------------------------------
# Layer the curriculum config on the user's normal opencode environment.
# We do NOT isolate XDG or use --pure: the studio shares the user's real
# providers, models, and connections and can save new ones. OPENCODE_CONFIG
# merges our skills/agent/METHOD; project config stays off so a downloaded
# course cannot smuggle its own config.
# Only point at a config that exists. mini has no curriculum config, and
# naming a missing file would make the engine complain on every launch.
[ -f "$STUDIO/opencode.json" ] && export OPENCODE_CONFIG="$STUDIO/opencode.json"
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export OPENCODE_DISABLE_AUTOUPDATE=1

# --- credentials: Sage when present, Zen public floor otherwise ----------
KEY="$(security find-generic-password -s is.sage.downes -w 2>/dev/null || true)"
if [ -n "$KEY" ]; then
  export DOWNES_SAGE_KEY="$KEY"
  export OPENCODE_CONFIG_CONTENT='{"model":"sage/downes-standard"}'
fi

[ -t 1 ] && printf '\033]0;Downes — the studio\007'
cd "$STUDIO"

# --- engine resolution ------------------------------------------------------
# An installed copy must be self-contained: the compiled engine is a Bun
# single-file executable, so nothing else needs to be on the machine. Look
# beside the install first (Homebrew stages it at libexec/bin), and only then
# fall back to a developer checkout.
case "$(uname -s)" in
  Darwin) OS="darwin" ;;
  Linux)  OS="linux" ;;
  *)      OS="unknown" ;;
esac
case "$(uname -m)" in
  arm64|aarch64) ARCH="arm64" ;;
  *)             ARCH="x64" ;;
esac

FORK="$HERE/../ai-ui-mini/packages/opencode"
BIN=""
for cand in \
  "${DOWNES_ENGINE:-}" \
  "$HERE/../bin/opencode" \
  "$HERE/../opencode-$OS-$ARCH/bin/opencode" \
  "$FORK/dist/opencode-$OS-$ARCH/bin/opencode"
do
  [ -n "$cand" ] && [ -x "$cand" ] && { BIN="$cand"; break; }
done

if [ -n "$BIN" ]; then
  exec "$BIN" "$@"
fi

# Developer convenience only. This path must never be reached on an installed
# copy — if it is, the payload was assembled wrong.
if [ -f "$FORK/src/index.ts" ] && [ -d "$FORK/node_modules/@opentui" ] && command -v bun >/dev/null 2>&1; then
  exec bun run --cwd "$FORK" --conditions=browser src/index.ts "$@"
fi

echo "Downes: the curriculum engine is missing from this install." >&2
echo "Reinstall with: brew reinstall sage-is/apps/downes" >&2
exit 1
