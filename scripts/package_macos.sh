#!/usr/bin/env bash
# Assemble a self-contained macOS payload for the Homebrew tap.
#
# The output tarball must run on a Mac that has nothing but Homebrew: no bun,
# no node, no opencode, no Xcode tools. The engine is a Bun single-file
# executable, so shipping that binary is sufficient — never a `bun run` path.
#
# Two products share this script and one Rust binary, differing only in bundle
# metadata and payload contents:
#
#   downes  the curriculum agent. Ships the studio template (skills, METHOD,
#           prompts), so the payload carries AGPL content.
#   mini    the bare Sage.is AI-UI mini platform. No curriculum, MIT only.
#
# Usage:  scripts/package_macos.sh [arm64|x64] [downes|mini]
# Output: dist/<product>-<version>-darwin-<arch>.tar.gz + its sha256
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FORK="$REPO/ai-ui-mini"
STUDIO_PKG="$FORK/packages/studio"

PRODUCT="${2:-downes}"
[ "$PRODUCT" = "downes" ] || [ "$PRODUCT" = "mini" ] || { echo "product must be downes or mini" >&2; exit 1; }

ARCH="${1:-}"
if [ -z "$ARCH" ]; then
  case "$(uname -m)" in
    arm64|aarch64) ARCH="arm64" ;;
    *)             ARCH="x64" ;;
  esac
fi
[ "$ARCH" = "arm64" ] || [ "$ARCH" = "x64" ] || { echo "arch must be arm64 or x64" >&2; exit 1; }

VERSION="$(python3 -c "import json;print(json.load(open('$STUDIO_PKG/src-tauri/tauri.conf.json'))['version'])")"
ENGINE="$FORK/packages/opencode/dist/opencode-darwin-$ARCH/bin/opencode"
OUT="$REPO/dist"
STAGE="$OUT/stage-$PRODUCT-$ARCH"

if [ "$PRODUCT" = "mini" ]; then
  APP_NAME="Sage.is mini"; WORKSPACE="SageMini"
  TAURI_ARGS=(--config src-tauri/tauri.mini.conf.json)
else
  APP_NAME="Downes"; WORKSPACE="Downes"
  TAURI_ARGS=()
fi

echo "==> $APP_NAME $VERSION, darwin-$ARCH"

# --- engine ----------------------------------------------------------------
if [ ! -x "$ENGINE" ]; then
  echo "==> building engine (not found at $ENGINE)"
  (cd "$FORK/packages/opencode" && bun run script/build.ts)
fi
[ -x "$ENGINE" ] || { echo "engine missing after build: $ENGINE" >&2; exit 1; }

# --- app -------------------------------------------------------------------
# Tauri names the release bundle by productName, not by arch.
APP="$STUDIO_PKG/src-tauri/target/release/bundle/macos/$APP_NAME.app"
APP_EXE="$APP/Contents/MacOS/downes-studio"
case "$ARCH" in arm64) WANT_ARCH="arm64" ;; x64) WANT_ARCH="x86_64" ;; esac

# Reuse is only safe when the bundle is for THIS arch and is not older than the
# sources. The path encodes productName alone — no architecture, no source
# identity — so a bare `[ -d "$APP" ]` silently ships a bundle built from other
# code or for another CPU. That is not hypothetical: a payload was assembled
# here from a bundle predating the Rust change it was supposed to carry.
REBUILD=""
if [ ! -d "$APP" ]; then
  REBUILD="no bundle yet"
elif ! lipo -archs "$APP_EXE" 2>/dev/null | tr ' ' '\n' | grep -qx "$WANT_ARCH"; then
  REBUILD="bundle is $(lipo -archs "$APP_EXE" 2>/dev/null || echo unreadable), want $WANT_ARCH"
elif [ -n "$(find "$STUDIO_PKG/src-tauri/src" "$STUDIO_PKG/frontend/src" \
             "$STUDIO_PKG/src-tauri/Cargo.toml" \
             "$STUDIO_PKG/src-tauri"/tauri*.conf.json \
             -type f -newer "$APP_EXE" -print -quit 2>/dev/null)" ]; then
  REBUILD="sources or config are newer than the bundle"
elif [ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' \
          "$APP/Contents/Info.plist" 2>/dev/null)" != "$VERSION" ]; then
  # The version lives in tauri.conf.json and is stamped into Info.plist at
  # bundle time. Bumping it touches no source file, so a source-mtime check
  # alone happily ships a v0.1.3 tarball containing a bundle that calls itself
  # v0.1.2 — which is exactly what happened on the first attempt at this
  # release.
  REBUILD="bundle is v$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' \
            "$APP/Contents/Info.plist" 2>/dev/null), releasing v$VERSION"
fi

if [ -n "$REBUILD" ]; then
  echo "==> building $APP_NAME.app (release) — $REBUILD"
  (cd "$STUDIO_PKG" && bunx tauri build --bundles app "${TAURI_ARGS[@]}")
fi
[ -d "$APP" ] || { echo "$APP_NAME.app missing after build: $APP" >&2; exit 1; }

# Prove the shipped bundle is the right architecture, not just that a build ran.
lipo -archs "$APP_EXE" 2>/dev/null | tr ' ' '\n' | grep -qx "$WANT_ARCH" \
  || { echo "$APP_NAME.app is not $WANT_ARCH: $(lipo -archs "$APP_EXE" 2>/dev/null)" >&2; exit 1; }

# --- stage -----------------------------------------------------------------
echo "==> staging"
rm -rf "$STAGE"
mkdir -p "$STAGE/bin" "$STAGE/launcher" "$STAGE/scripts"

cp "$ENGINE" "$STAGE/bin/opencode"
chmod 0755 "$STAGE/bin/opencode"

cp -R "$APP" "$STAGE/$APP_NAME.app"

# Product marker: the Rust binary is identical in both apps, so it reads this
# to know which workspace folder to use.
printf '%s\n' "$WORKSPACE" > "$STAGE/product"

# Launcher, shim, and the studio template the first run installs from.
cp "$REPO/launcher/downes.sh" "$STAGE/launcher/downes.sh"
chmod 0755 "$STAGE/launcher/downes.sh"
# The Layer-3 profile must travel with the launcher. Without it the sandbox
# guard finds no profile and silently runs unfenced — the failure mode is an
# install that claims containment and has none.
cp "$REPO/launcher/downes.sb" "$STAGE/launcher/downes.sb"
chmod 0644 "$STAGE/launcher/downes.sb"
# The Terminal shim is Downes-branded and only serves the terminal-first
# flow; shipping it in mini would drop a stray "Downes.app" into the
# platform payload.
if [ "$PRODUCT" = "downes" ]; then
  cp -R "$REPO/launcher/Downes.app" "$STAGE/launcher/Downes.app"
  chmod 0755 "$STAGE/launcher/Downes.app/Contents/MacOS/downes-app"
fi
cp "$REPO/scripts/install_studio.sh" "$STAGE/scripts/install_studio.sh"
chmod 0755 "$STAGE/scripts/install_studio.sh"
# Curriculum template is Downes-only. Shipping it in mini would put AGPL
# content in an MIT artifact and give the platform an agent it does not claim
# to have.
if [ "$PRODUCT" = "downes" ]; then
  # Courses are user output, and studio/.downes/courses/ is gitignored. A
  # plain copy takes whatever the build machine happens to have: v0.1.2 shipped
  # an 8-file test course generated on 2026-08-21, which install_studio.sh then
  # rsynced into every teacher's studio. The template carries tracked content
  # only.
  rsync -a --exclude '.downes/courses/' "$REPO/studio/" "$STAGE/studio/"

  # Reproducibility guard: two people building the same tag must get the same
  # payload. Anything else untracked under studio/ is local state, not template.
  if git -C "$REPO" rev-parse >/dev/null 2>&1; then
    STRAY="$(git -C "$REPO" ls-files --others --ignored --exclude-standard -- studio \
             | grep -v '^studio/\.downes/courses/' || true)"
    if [ -n "$STRAY" ]; then
      echo "payload would ship untracked template content:" >&2
      printf '  %s\n' $STRAY >&2
      exit 1
    fi
  fi
fi

# --- self-containment check ------------------------------------------------
# Prove it, do not assume it: the engine must not be a shell shim pointing at
# a runtime, and nothing in the payload may reference the developer checkout.
echo "==> checking self-containment"
file "$STAGE/bin/opencode" | grep -q "Mach-O" \
  || { echo "engine is not a Mach-O executable" >&2; exit 1; }
if grep -rIl "Documents/Projects/GitHub" "$STAGE" 2>/dev/null | grep -q .; then
  echo "payload references the developer checkout:" >&2
  grep -rIl "Documents/Projects/GitHub" "$STAGE" >&2
  exit 1
fi

# --- tar -------------------------------------------------------------------
TARBALL="$OUT/$PRODUCT-$VERSION-darwin-$ARCH.tar.gz"
echo "==> writing $TARBALL"
tar -czf "$TARBALL" -C "$STAGE" .
rm -rf "$STAGE"

SHA="$(shasum -a 256 "$TARBALL" | awk '{print $1}')"
SIZE="$(du -h "$TARBALL" | awk '{print $1}')"
echo
echo "  $TARBALL"
echo "  size   $SIZE"
echo "  sha256 $SHA"
