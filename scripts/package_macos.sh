#!/usr/bin/env bash
# Assemble a self-contained macOS payload for the Homebrew tap.
#
# The output tarball must run on a Mac that has nothing but Homebrew: no bun,
# no node, no opencode, no Xcode tools. The engine is a Bun single-file
# executable, so shipping that binary is sufficient — never a `bun run` path.
#
# Usage:  scripts/package_macos.sh [arm64|x64]        (default: this machine)
# Output: dist/downes-<version>-darwin-<arch>.tar.gz  + its sha256
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FORK="$REPO/ai-ui-mini"
STUDIO_PKG="$FORK/packages/studio"

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
STAGE="$OUT/stage-$ARCH"

echo "==> Downes $VERSION, darwin-$ARCH"

# --- engine ----------------------------------------------------------------
if [ ! -x "$ENGINE" ]; then
  echo "==> building engine (not found at $ENGINE)"
  (cd "$FORK/packages/opencode" && bun run script/build.ts)
fi
[ -x "$ENGINE" ] || { echo "engine missing after build: $ENGINE" >&2; exit 1; }

# --- app -------------------------------------------------------------------
# Tauri names the release bundle by productName, not by arch.
APP="$STUDIO_PKG/src-tauri/target/release/bundle/macos/Downes.app"
if [ ! -d "$APP" ]; then
  echo "==> building Downes.app (release)"
  (cd "$STUDIO_PKG" && bunx tauri build --bundles app)
fi
[ -d "$APP" ] || { echo "Downes.app missing after build: $APP" >&2; exit 1; }

# --- stage -----------------------------------------------------------------
echo "==> staging"
rm -rf "$STAGE"
mkdir -p "$STAGE/bin" "$STAGE/launcher" "$STAGE/scripts"

cp "$ENGINE" "$STAGE/bin/opencode"
chmod 0755 "$STAGE/bin/opencode"

cp -R "$APP" "$STAGE/Downes.app"

# Launcher, shim, and the studio template the first run installs from.
cp "$REPO/launcher/downes.sh" "$STAGE/launcher/downes.sh"
cp -R "$REPO/launcher/Downes.app" "$STAGE/launcher/Downes.app"
chmod 0755 "$STAGE/launcher/downes.sh" "$STAGE/launcher/Downes.app/Contents/MacOS/downes-app"
cp "$REPO/scripts/install_studio.sh" "$STAGE/scripts/install_studio.sh"
chmod 0755 "$STAGE/scripts/install_studio.sh"
cp -R "$REPO/studio" "$STAGE/studio"

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
TARBALL="$OUT/downes-$VERSION-darwin-$ARCH.tar.gz"
echo "==> writing $TARBALL"
tar -czf "$TARBALL" -C "$STAGE" .
rm -rf "$STAGE"

SHA="$(shasum -a 256 "$TARBALL" | awk '{print $1}')"
SIZE="$(du -h "$TARBALL" | awk '{print $1}')"
echo
echo "  $TARBALL"
echo "  size   $SIZE"
echo "  sha256 $SHA"
