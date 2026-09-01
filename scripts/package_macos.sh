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
  APP_NAME="SAGE.IS mini"; WORKSPACE="SageMini"
  TAURI_ARGS=(--config src-tauri/tauri.mini.conf.json)
else
  APP_NAME="Downes"; WORKSPACE="Downes"
  TAURI_ARGS=()
fi

echo "==> $APP_NAME $VERSION, darwin-$ARCH"

# --- engine ----------------------------------------------------------------
# Pin the channel. Left unset, the fork's build script falls back to the
# current GIT BRANCH NAME (packages/script/src/index.ts:30), so the shipped
# version string and the database filename both depend on which branch the
# release happened to be cut from — v0.1.3 shipped "downes/v1" only because
# that was the branch at the time, and a build on develop produced "develop".
export OPENCODE_CHANNEL="${OPENCODE_CHANNEL:-downes/v1}"

if [ ! -x "$ENGINE" ]; then
  echo "==> building engine (not found at $ENGINE), channel $OPENCODE_CHANNEL"
  (cd "$FORK/packages/opencode" && bun run script/build.ts)
fi
[ -x "$ENGINE" ] || { echo "engine missing after build: $ENGINE" >&2; exit 1; }

# The engine must agree with the channel we asked for, or the database name and
# the version string are someone else's accident.
ENGINE_V="$("$ENGINE" --version 2>/dev/null || true)"
case "$ENGINE_V" in
  *"$OPENCODE_CHANNEL"*) : ;;
  *) echo "engine reports '$ENGINE_V', expected channel '$OPENCODE_CHANNEL'." >&2
     echo "  Delete $FORK/packages/opencode/dist and re-run to rebuild it." >&2
     exit 1 ;;
esac

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
# Everything the shell needs goes INSIDE the bundle, under Contents/Resources.
# A Mac app has to be self-contained: the cask's `app` stanza moves the .app to
# ~/Applications on its own, and anything left as a sibling is left behind.
# lib.rs:payload_roots() looks in Contents/Resources for exactly this reason.
echo "==> staging"
rm -rf "$STAGE"
mkdir -p "$STAGE"

cp -R "$APP" "$STAGE/$APP_NAME.app"
RES="$STAGE/$APP_NAME.app/Contents/Resources"
mkdir -p "$RES/bin" "$RES/launcher" "$RES/scripts"

cp "$ENGINE" "$RES/bin/opencode"
chmod 0755 "$RES/bin/opencode"

# Product marker: one Rust binary ships in both apps and reads this to know
# which workspace folder it owns.
printf '%s\n' "$WORKSPACE" > "$RES/product"

cp "$REPO/launcher/downes.sh" "$RES/launcher/downes.sh"
chmod 0755 "$RES/launcher/downes.sh"
# The Layer-3 profile must travel with the launcher, or the sandbox guard finds
# no profile and silently runs unfenced.
cp "$REPO/launcher/downes.sb" "$RES/launcher/downes.sb"
chmod 0644 "$RES/launcher/downes.sb"
cp "$REPO/scripts/install_studio.sh" "$RES/scripts/install_studio.sh"
chmod 0755 "$RES/scripts/install_studio.sh"

# Curriculum template is Downes-only. Shipping it in mini would put AGPL
# content in an MIT artifact and give the platform an agent it does not claim
# to have.
if [ "$PRODUCT" = "downes" ]; then
  # Courses are user output, and studio/.downes/courses/ is gitignored. A plain
  # copy takes whatever the build machine happens to have: v0.1.2 shipped an
  # 8-file test course into every teacher's studio that way.
  rsync -a --exclude '.downes/courses/' "$REPO/studio/" "$RES/studio/"

  # Reproducibility: two people building the same tag must get the same payload.
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

# Sign inside-out, then seal the bundle.
#
# The engine is a Bun single-file executable and ships with a signature macOS
# already considers modified — Bun appends the payload after signing. `--deep`
# does NOT fix it: --deep descends into nested bundles and frameworks, not loose
# Mach-O files under Resources. A quarantined app containing a binary with a
# broken seal does not merely warn, it hangs on exec, which is how v0.1.4 first
# shipped with a launcher that never returned.
echo "==> signing engine and $APP_NAME.app"
codesign --force --sign - "$RES/bin/opencode"
codesign --verify "$RES/bin/opencode" \
  || { echo "engine failed signature verification" >&2; exit 1; }

codesign --force --sign - "$STAGE/$APP_NAME.app"
codesign --verify --deep "$STAGE/$APP_NAME.app" \
  || { echo "$APP_NAME.app failed signature verification after staging" >&2; exit 1; }

# --- self-containment check ------------------------------------------------
# Prove it, do not assume it: the engine must not be a shell shim pointing at
# a runtime, and nothing in the payload may reference the developer checkout.
echo "==> checking self-containment"
file "$STAGE/$APP_NAME.app/Contents/Resources/bin/opencode" | grep -q "Mach-O" \
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
