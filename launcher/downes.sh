#!/usr/bin/env bash
# Downes launcher — pins the studio, isolates all opencode state under it,
# applies the Layer-3 fence, and boots the agent. This is the TERMINAL entry
# point.
#
# It is not the only one. The studio app spawns the same engine from
# ai-ui-mini/packages/studio/src-tauri/src/lib.rs (isolate_state, sandbox_prefix)
# and must configure it identically. Anything changed here — XDG roots, skill
# flags, sandbox params, the DOWNES_* switches — has a sibling there. The two
# drifting apart is how the studio ended up running unfenced while this file
# claimed the product was contained.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OS_UNAME="$(uname -s)"

# Which product this payload is. Downes ships the curriculum template; the
# bare Sage.is mini platform does not, and uses its own workspace folder.
# Absent marker means Downes, so existing installs are unaffected.
WORKSPACE="Downes"
[ -f "$HERE/../product" ] && WORKSPACE="$(tr -d '[:space:]' < "$HERE/../product")"

STUDIO="${DOWNES_STUDIO:-$HOME/$WORKSPACE}"
# Physical path, before anything is derived from it.
# The macOS sandbox canonicalizes a path before matching it against a subpath rule, so a studio
# reached through a symlink — including anything under /tmp, which is itself a
# symlink to /private/tmp — would never match its own allow rule, and the one
# writable tree in the profile would be silently unwritable.
mkdir -p "$STUDIO" 2>/dev/null || true
STUDIO="$(cd "$STUDIO" 2>/dev/null && pwd -P || echo "$STUDIO")"
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

  # The engine's folder inside each XDG root is named after its compiled-in
  # channel (core/src/global.ts): "opencode" before v0.1.4, "downes" from here
  # on. An existing studio's sessions live under the old name, so bring them
  # with us or the teacher opens the studio to an empty session list.
  for _x in "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_STATE_HOME" "$XDG_CACHE_HOME"; do
    if [ -d "$_x/opencode" ] && [ ! -e "$_x/downes" ]; then
      mv "$_x/opencode" "$_x/downes" 2>/dev/null || true
    fi
  done
  unset _x

  # Our state must never be committable. The studio is the folder we tell
  # teachers to keep their courses in and share with colleagues, and the seed
  # below puts real provider keys inside it — a `git init && git add -A` in
  # ~/Downes would otherwise stage them.
  if ! grep -qs '^\.downes/xdg/' "$STUDIO/.gitignore" 2>/dev/null; then
    printf '%s\n' '.downes/xdg/' >> "$STUDIO/.gitignore"
  fi

  # Seed the credential store once from the user's real opencode, so
  # isolation costs nobody a second login. They diverge after this: a
  # provider added here will not show up in a stock opencode session.
  _seed="$XDG_DATA_HOME/downes/auth.json"
  _real="$HOME/.local/share/opencode/auth.json"
  if [ ! -f "$_seed" ] && [ -f "$_real" ]; then
    mkdir -p "$(dirname "$_seed")"
    cp "$_real" "$_seed" && chmod 600 "$_seed"
  fi
  unset _seed _real

  # --- one-time reclaim from the shared opencode store --------------------
  # Builds before v0.1.3 had no XDG isolation, so our engine wrote its
  # database straight into ~/.local/share/opencode next to a stock opencode's
  # own. Two databases, two schemas, one directory, and an error message that
  # named neither — that cost a colleague a morning's diagnosis, and
  # `brew uninstall` does not clean it up.
  #
  # Our file is identifiable: the engine names the database after its
  # compiled-in channel (core/src/database/database.ts), which for this fork
  # is downes/v1 → opencode-downes-v1.db. Stock opencode ships channel
  # latest/beta/prod and uses the unsuffixed opencode.db, which we never touch.
  # How many sessions a database holds. Opened immutable so a live writer is
  # never disturbed and no WAL is created. Empty string when unreadable.
  _session_count() {
    command -v sqlite3 >/dev/null 2>&1 || return 0
    sqlite3 "file:$1?immutable=1" "select count(*) from session;" 2>/dev/null || true
  }

  reclaim_shared_store() {
    local shared="$HOME/.local/share/opencode" mine="$XDG_DATA_HOME/downes"
    local f base moved=0 theirs mine_n

    [ -d "$shared" ] || return 0

    for f in "$shared"/opencode-downes-*.db; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      mkdir -p "$mine"

      if [ ! -f "$mine/$base" ]; then
        # Nothing here yet: take it, WAL and all. Safe even if a process holds
        # it, because the destination is empty — but skip a live one anyway so
        # we never move a file mid-write.
        if command -v lsof >/dev/null 2>&1 && lsof -- "$f" >/dev/null 2>&1; then
          echo "Downes: $base is in use; will reclaim it on a later launch." >&2
          continue
        fi
        mv "$f" "$mine/$base" 2>/dev/null || continue
        mv "$f-shm" "$mine/$base-shm" 2>/dev/null || true
        mv "$f-wal" "$mine/$base-wal" 2>/dev/null || true
        moved=1
        continue
      fi

      # Both exist. Decide on CONTENT, never on which file happens to be
      # present: isolation shipped a release before this reclaim did, so the
      # studio's copy is usually the newer-but-emptier one, and picking it
      # silently retires a term's worth of a teacher's sessions.
      theirs="$(_session_count "$f")"
      mine_n="$(_session_count "$mine/$base")"

      if [ -n "$theirs" ] && [ -n "$mine_n" ] && [ "$theirs" -gt "$mine_n" ] 2>/dev/null; then
        if command -v lsof >/dev/null 2>&1 && lsof -- "$f" >/dev/null 2>&1; then
          echo "Downes: $base is in use; will reclaim it on a later launch." >&2
          continue
        fi
        # The stray is richer. Park the sparse studio copy, never delete it.
        mv "$mine/$base" "$mine/$base.sparse" 2>/dev/null || continue
        rm -f "$mine/$base-shm" "$mine/$base-wal" 2>/dev/null
        mv "$f" "$mine/$base" 2>/dev/null || continue
        mv "$f-shm" "$mine/$base-shm" 2>/dev/null || true
        mv "$f-wal" "$mine/$base-wal" 2>/dev/null || true
        echo "Downes: recovered $theirs sessions an older build left in your" >&2
        echo "  opencode folder. The studio's $mine_n-session copy is kept as" >&2
        echo "  $base.sparse in case you want it." >&2
        moved=1
      else
        # Studio copy is as rich or richer, or neither could be read. Move the
        # stray out of the shared folder but keep it — deleting a teacher's
        # only copy on a guess is not ours to do.
        mv "$f" "$mine/$base.from-shared-store" 2>/dev/null || continue
        rm -f "$f-shm" "$f-wal" 2>/dev/null
        echo "Downes: an older build left $base in your opencode folder." >&2
        echo "  Moved it into the studio as $base.from-shared-store; your" >&2
        echo "  current sessions are untouched." >&2
        moved=1
      fi
    done

    # Each branch above reports what it actually did; a generic trailer here
    # only contradicted them.
    [ "$moved" = 1 ] && [ -n "${DOWNES_DEBUG:-}" ] && echo "Downes: reclaim complete." >&2
    return 0
  }
  reclaim_shared_store
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
# The model pin and the public-tier key are delivered HERE rather than in
# $STUDIO/opencode.json, because that file sits at the root of a directory the
# teacher opens in other tools. opencode walks up from its working directory
# collecting opencode.json unless OPENCODE_DISABLE_PROJECT_CONFIG is set — we
# set it, a stock opencode does not — so anything left in that file is adopted
# by someone else's session. Model, small_model and the provider key are the
# three that repoint a stock user's account and billing rather than merely
# restricting them, so they travel by env, which only our engine reads.
# OPENCODE_CONFIG_CONTENT is merged last (opencode/src/config/config.ts:468),
# so it wins over anything in the file.
KEY="$(security find-generic-password -s is.sage.downes -w 2>/dev/null || true)"
if [ -n "$KEY" ]; then
  export DOWNES_SAGE_KEY="$KEY"
  export OPENCODE_CONFIG_CONTENT='{"model":"sage/downes-standard"}'
else
  export OPENCODE_CONFIG_CONTENT='{"model":"opencode/nemotron-3.5-lightning-free","small_model":"opencode/big-pickle","provider":{"opencode":{"options":{"apiKey":"public"}}}}'
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
  # The two switches contradict each other: sharing state puts auth.json and
  # the database back under ~/.local/share/opencode, which the profile does
  # not make writable. Left uncoupled, the opt-out produces an engine that
  # cannot open its own log, and the error never mentions the sandbox. Refuse
  # instead, and name the flag that makes the trade explicit.
  if [ "${DOWNES_SHARE_STATE:-0}" = "1" ]; then
    echo "Downes: DOWNES_SHARE_STATE=1 needs DOWNES_NO_SANDBOX=1 as well." >&2
    echo "  Shared state lives outside the studio, and the sandbox only" >&2
    echo "  permits writes inside it. Set both, or neither." >&2
    exit 2
  fi
  if [ -f "$PROFILE" ] && command -v sandbox-exec >/dev/null 2>&1; then
    # TMPDIR must be the physical path for the same reason as STUDIO above:
    # /var/folders/... resolves through a symlink to /private/var/folders/...,
    # and the sandbox matches the resolved path. Passing it raw makes the TMP
    # allow rule dead, and every temp write inside the fence — mktemp, a bash
    # heredoc, any compiler — fails with EPERM.
    TMPPHYS="$(cd "${TMPDIR:-/tmp}" 2>/dev/null && pwd -P || echo /private/tmp)"
    SANDBOX=(sandbox-exec
             -D "STUDIO=$STUDIO"
             -D "TMP=$TMPPHYS"
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
