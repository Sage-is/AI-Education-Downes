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
if [ ! -d "$APP" ]; then
  echo "==> building $APP_NAME.app (release)"
  (cd "$STUDIO_PKG" && bunx tauri build --bundles app "${TAURI_ARGS[@]}")
fi
[ -d "$APP" ] || { echo "$APP_NAME.app missing after build: $APP" >&2; exit 1; }

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
  cp -R "$REPO/studio" "$STAGE/studio"
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
