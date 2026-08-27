#!/usr/bin/env bash
# Downes launcher — pins the studio, isolates all opencode state under it,
# and boots the agent. The single source of truth for environment,
# bootstrap, credentials, and (Checkpoint 3) the sandbox prefix.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OS_UNAME="$(uname -s)"

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
mkdir -p "$DHOME/config/themes" \
         "$DHOME/xdg/config" "$DHOME/xdg/data" "$DHOME/xdg/state" "$DHOME/xdg/cache"

# --- state isolation -----------------------------------------------------
# Every product's state resolves through xdg-basedir under a hardcoded app
# name of "opencode" (packages/core/src/global.ts). Left alone, Downes, mini
# and a stock opencode install share one auth.json, one opencode.db and one
# lockfile — last writer wins. Pointing XDG at the studio gives each product
# its own, and is also what makes Layer-3 possible at all: downes.sb permits
# writes only under STUDIO, so state in ~/.local/share would be denied the
# moment the sandbox is switched on.
#
# DOWNES_SHARE_STATE=1 opts back out to the shared home store.
if [ "${DOWNES_SHARE_STATE:-0}" != "1" ]; then
  export XDG_CONFIG_HOME="$DHOME/xdg/config"
  export XDG_DATA_HOME="$DHOME/xdg/data"
  export XDG_STATE_HOME="$DHOME/xdg/state"
  export XDG_CACHE_HOME="$DHOME/xdg/cache"

  # Seed the credential store once from the user's real opencode, so
  # isolation costs nobody a second login. They diverge after this: a
  # provider added here will not show up in a stock opencode session.
  _seed="$XDG_DATA_HOME/opencode/auth.json"
  _real="$HOME/.local/share/opencode/auth.json"
  if [ ! -f "$_seed" ] && [ -f "$_real" ]; then
    mkdir -p "$(dirname "$_seed")"
    cp "$_real" "$_seed" && chmod 600 "$_seed"
  fi
  unset _seed _real
fi

# Keep the machine owner's personal Claude Code setup out of a teacher's
# session. Two separate channels, and XDG isolation closes neither of them —
# both resolve against the real home directory, not the XDG dirs:
#   - skills: ~/.claude/skills and ~/.agents/skills are scanned and loaded
#     (skill/index.ts:186)
#   - prompt: ~/.claude/CLAUDE.md is attached as an instruction file, and so
#     is a CLAUDE.md sitting in the project — which a downloaded course could
#     ship (session/instruction.ts:62,66)
# The broad flag covers prompt and skills together.
export OPENCODE_DISABLE_EXTERNAL_SKILLS=1
export OPENCODE_DISABLE_CLAUDE_CODE=1

# --- config layer --------------------------------------------------------
# OPENCODE_CONFIG merges our skills/agent/METHOD; project config stays off so
# a downloaded course cannot smuggle its own config.
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

# --- desktop entry ----------------------------------------------------------
# Homebrew cannot do this from the formula. post_install runs with HOME
# replaced by a temp dir Homebrew then deletes, inside a sandbox that permits
# writes only under the formula prefix — so the symlink reports success and
# creates nothing. Here we are the user, with a real HOME and no sandbox.
#
# Idempotent, and silent when there is nothing to do. In a developer checkout
# there is no .app beside the launcher's parent, so this is a no-op.
link_app() {
  local src="" cand dest bundle root keg name tail optroot
  # Canonical, so the symlink target reads cleanly and the idempotency check
  # below can compare it literally.
  root="$(cd "$HERE/.." 2>/dev/null && pwd)" || return 0

  # Under Homebrew that canonical path lands in the VERSIONED keg
  # (…/Cellar/downes/0.1.2/libexec), and brew deletes the old keg on upgrade.
  # A symlink pointing there dangles the moment someone upgrades and then
  # double-clicks the app. Rewrite to the version-independent opt path.
  case "$root" in
    */Cellar/*)
      keg="${root#*/Cellar/}"        # downes/0.1.2/libexec
      name="${keg%%/*}"              # downes
      tail="${keg#*/}"               # 0.1.2/libexec
      tail="${tail#*/}"              # libexec
      optroot="${root%%/Cellar/*}/opt/$name"
      [ -n "$tail" ] && optroot="$optroot/$tail"
      [ -d "$optroot" ] && root="$optroot"
      ;;
  esac

  for cand in "$root"/*.app; do
    [ -d "$cand" ] && { src="$cand"; break; }
  done
  [ -n "$src" ] || return 0

  mkdir -p "$HOME/Applications" 2>/dev/null || return 0
  dest="$HOME/Applications/$(basename "$src")"

  # Already pointing at this install.
  [ "$(readlink "$dest" 2>/dev/null)" = "$src" ] && return 0

  # A real directory here shadows the install: it is a hand-copied bundle with
  # no engine beside it, so engine resolution walks past it and falls through
  # to a developer checkout that exists only on the build machine. That is the
  # "empty studio / sidecar unreachable" failure. Replace it — but only once
  # it identifies as ours. Never a blind rm under ~/Applications.
  if [ -d "$dest" ] && [ ! -L "$dest" ]; then
    bundle="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' \
              "$dest/Contents/Info.plist" 2>/dev/null || true)"
    case "$bundle" in
      is.sage.*) rm -rf "$dest" ;;
      *)         return 0 ;;
    esac
  fi

  ln -sfn "$src" "$dest" 2>/dev/null || true
}
[ "$OS_UNAME" = "Darwin" ] && link_app

[ -t 1 ] && printf '\033]0;Downes — the studio\007'
cd "$STUDIO"

# --- engine resolution ------------------------------------------------------
# An installed copy must be self-contained: the compiled engine is a Bun
# single-file executable, so nothing else needs to be on the machine. Look
# beside the install first (Homebrew stages it at libexec/bin), and only then
# fall back to a developer checkout.
case "$OS_UNAME" in
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

# --- Layer-3 containment ----------------------------------------------------
# downes.sb is deny-default for writes: the studio and TMP, nothing else. That
# is only survivable because the state isolation above moved the engine's
# auth.json, database and logs under the studio. Wiring this without that
# change denies the engine its own credentials on first launch.
#
# One seam, one backend. Linux (Landlock) and Windows are unclaimed — see
# docs/decisions/. DOWNES_NO_SANDBOX=1 bypasses for debugging.
SANDBOX=()
PROFILE="$HERE/downes.sb"
if [ "${DOWNES_NO_SANDBOX:-0}" != "1" ] && [ "$OS" = "darwin" ]; then
  if [ -f "$PROFILE" ] && command -v sandbox-exec >/dev/null 2>&1; then
    SANDBOX=(sandbox-exec
             -D "STUDIO=$STUDIO"
             -D "TMP=${TMPDIR:-/tmp}"
             -D "HOMEDIR=$HOME"
             -f "$PROFILE")
  else
    # Never fail closed into a silent lie: if the profile did not travel with
    # the payload, say so rather than running unfenced while the copy claims
    # containment.
    echo "Downes: sandbox profile not found; running unfenced." >&2
  fi
fi

# ${SANDBOX[@]+...} guards the empty-array expansion — macOS still ships
# bash 3.2, where a bare "${SANDBOX[@]}" is an unbound variable under `set -u`.
if [ -n "$BIN" ]; then
  exec ${SANDBOX[@]+"${SANDBOX[@]}"} "$BIN" "$@"
fi

# Developer convenience only. This path must never be reached on an installed
# copy — if it is, the payload was assembled wrong.
if [ -f "$FORK/src/index.ts" ] && [ -d "$FORK/node_modules/@opentui" ] && command -v bun >/dev/null 2>&1; then
  exec ${SANDBOX[@]+"${SANDBOX[@]}"} bun run --cwd "$FORK" --conditions=browser src/index.ts "$@"
fi

echo "Downes: the curriculum engine is missing from this install." >&2
echo "Reinstall with: brew reinstall sage-is/apps/downes" >&2
exit 1
