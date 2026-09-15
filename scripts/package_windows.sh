#!/usr/bin/env bash
# Assemble the Downes installer for Windows.
#
# The fork builds SAGE.IS mini for Windows on its own (see
# ai-ui-mini/packages/studio/README.md): engine, product marker, NSIS. Downes is
# that same shell plus the curriculum template -- skills, METHOD, prompts, and
# the opencode.json whose default_agent is "downes". The template is AGPL
# content and must not live in the MIT fork, so, as on macOS, this repo adds it.
# Built without it, the app opens on opencode's Build agent: ensure_studio()
# finds no template and writes mini's bare config instead.
#
# Run from Git Bash. Plain `bash` on a Windows PATH is usually WSL, which
# builds nothing that runs here.
#
# Usage:  scripts/package_windows.sh
# Output: dist/downes-<version>-windows-<arch>-setup.exe + its sha256
set -euo pipefail

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) : ;;
  *) echo "run this from Git Bash on Windows (uname: $(uname -s))" >&2; exit 1 ;;
esac

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FORK="$REPO/ai-ui-mini"
STUDIO_PKG="$FORK/packages/studio"
TAURI_DIR="$STUDIO_PKG/src-tauri"

# Host arch only: stage-payload.ts stages the engine for the machine it runs on,
# and a cross-arch bundle would carry an engine for the wrong CPU.
case "${PROCESSOR_ARCHITEW6432:-${PROCESSOR_ARCHITECTURE:-}}" in
  ARM64) ARCH="arm64" ;;
  *)     ARCH="x64" ;;
esac

VERSION="$(bun -e "console.log(require('$(cygpath -m "$TAURI_DIR")/tauri.conf.json').version)")"
ENGINE="$FORK/packages/opencode/dist/opencode-windows-$ARCH/bin/opencode.exe"
OUT="$REPO/dist"
STAGE="$OUT/stage-downes-windows-$ARCH"

echo "==> Downes $VERSION, windows-$ARCH"

# --- engine ----------------------------------------------------------------
# Pinned, as on macOS: unset, the fork's build script takes the channel from the
# current git branch, and a submodule checkout is on a detached HEAD -- so the
# channel, the version string and the database filename would all be empty.
export OPENCODE_CHANNEL="${OPENCODE_CHANNEL:-downes/v1}"

ENGINE_WHY=""
if [ ! -f "$ENGINE" ]; then
  ENGINE_WHY="not found at $ENGINE"
elif [ -n "$(find "$FORK/packages" \( -name node_modules -o -name dist -o -path "$STUDIO_PKG" \) -prune \
             -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.json' \) -newer "$ENGINE" -print -quit)" ]; then
  ENGINE_WHY="sources are newer than the engine"
fi
if [ -n "$ENGINE_WHY" ]; then
  echo "==> building engine ($ENGINE_WHY), channel $OPENCODE_CHANNEL"
  (cd "$FORK" && bun packages/opencode/script/build.ts --single)
fi
[ -f "$ENGINE" ] || { echo "engine missing after build: $ENGINE" >&2; exit 1; }

ENGINE_V="$("$ENGINE" --version 2>/dev/null || true)"
case "$ENGINE_V" in
  *"$OPENCODE_CHANNEL"*) : ;;
  *) echo "engine reports '$ENGINE_V', expected channel '$OPENCODE_CHANNEL'." >&2
     echo "  Delete $FORK/packages/opencode/dist and re-run to rebuild it." >&2
     exit 1 ;;
esac

# --- stage -----------------------------------------------------------------
echo "==> staging"
rm -rf "$STAGE"
mkdir -p "$STAGE/licenses"

# Tracked files only. Courses are user output and studio/.downes/courses/ is
# gitignored; v0.1.2 shipped a test course to every teacher by copying the
# folder wholesale. An untracked file is refused rather than dropped, so a skill
# someone forgot to `git add` fails the build instead of silently not shipping.
STRAY="$(git -C "$REPO" ls-files --others -- studio | grep -v '^studio/\.downes/courses/' || true)"
if [ -n "$STRAY" ]; then
  echo "studio/ has untracked files; commit or remove them:" >&2
  printf '  %s\n' $STRAY >&2
  exit 1
fi
(cd "$REPO" && git ls-files -z -- studio | xargs -0 cp --parents -t "$STAGE")
[ -f "$STAGE/studio/opencode.json" ] || { echo "template has no opencode.json" >&2; exit 1; }
grep -q '"default_agent": "downes"' "$STAGE/studio/opencode.json" \
  || { echo "template opencode.json does not default to the downes agent" >&2; exit 1; }

# OFL 1.1 clause 2: the font's licence travels with the bundle that carries it.
FONT_LICENSE="$STUDIO_PKG/frontend/src/fonts/LICENSE-AnnotationMono.txt"
[ -f "$FONT_LICENSE" ] || { echo "font licence not found at $FONT_LICENSE" >&2; exit 1; }
cp "$FONT_LICENSE" "$STAGE/licenses/"

# Merged over tauri.conf.json (already Downes: name, identifier, icons) and the
# auto-merged tauri.windows.conf.json (NSIS, engine, product marker). Resources
# are a map, so these keys add to the engine and marker rather than replace
# them. A directory key is walked with its structure kept, .downes included; a
# glob would flatten it. Absolute paths, because relative ones resolve against
# src-tauri, not this file.
#
# The installer icons are overridden because the Windows config names mini's.
# The header and sidebar bitmaps are not: they are drawn by the fork's
# make-installer-art.py, which knows only the mini mark and wordmark.
CFG="$STAGE/tauri.downes.windows.json"
cat > "$CFG" <<EOF
{
  "bundle": {
    "windows": {
      "nsis": {
        "installerIcon": "$(cygpath -m "$TAURI_DIR/icons/icon.ico")",
        "uninstallerIcon": "$(cygpath -m "$TAURI_DIR/icons/icon.ico")"
      }
    },
    "resources": {
      "$(cygpath -m "$STAGE/studio")": "studio",
      "$(cygpath -m "$STAGE/licenses")": "licenses"
    }
  }
}
EOF

# --- build -----------------------------------------------------------------
# A copy running from target\ holds its exe and engine open, and the build has
# to overwrite both: the cargo build script copies the engine there and the
# bundler patches the exe. Windows reports that as a bare "os error 32" minutes
# into the build, so refuse up front and name the culprit. Get-Process exits
# non-zero when it finds nothing, which is the normal case, hence `|| true`.
RUNNING="$(powershell.exe -NoProfile -Command \
  "Get-Process downes-studio,opencode -ErrorAction SilentlyContinue |
   Where-Object { \$_.Path -like '$(cygpath -w "$TAURI_DIR/target")*' } |
   ForEach-Object { '{0} {1}' -f \$_.Id, \$_.Path }" | tr -d '\r' || true)"
if [ -n "$RUNNING" ]; then
  echo "close the studio running from the build tree first:" >&2
  printf '  %s\n' "$RUNNING" >&2
  exit 1
fi

# DOWNES_PRODUCT is read by stage-payload.ts, which the Windows config runs as
# beforeBuildCommand; unset, it marks the bundle SAGE.ISmini and the app writes
# into ~/SAGE.ISmini while calling itself Downes.
echo "==> building Downes (NSIS)"
(cd "$STUDIO_PKG" && DOWNES_PRODUCT=Downes bunx tauri build --config "$(cygpath -m "$CFG")")

# tauri-build copies the resources beside target/release/downes-studio.exe from
# the same merged config the bundler reads, so this proves the template made it
# into the bundle's resource list without unpacking the installer.
RELEASE="$TAURI_DIR/target/release"
[ -f "$RELEASE/studio/opencode.json" ] && [ -d "$RELEASE/studio/.downes/skills" ] \
  || { echo "the template did not reach the bundle's resources" >&2; exit 1; }
[ "$(tr -d '\r\n' < "$RELEASE/product")" = "Downes" ] \
  || { echo "product marker is '$(cat "$RELEASE/product")', expected Downes" >&2; exit 1; }

SETUP="$TAURI_DIR/target/release/bundle/nsis/Downes_${VERSION}_${ARCH}-setup.exe"
[ -f "$SETUP" ] || { echo "installer missing after build: $SETUP" >&2; exit 1; }

INSTALLER="$OUT/downes-$VERSION-windows-$ARCH-setup.exe"
cp "$SETUP" "$INSTALLER"
rm -rf "$STAGE"

echo
echo "  $INSTALLER"
echo "  size   $(du -h "$INSTALLER" | awk '{print $1}')"
echo "  sha256 $(sha256sum "$INSTALLER" | awk '{print $1}')"
