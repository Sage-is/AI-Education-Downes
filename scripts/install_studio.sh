#!/usr/bin/env bash
# Install (or refresh) the Downes studio. Additive only — never deletes
# teacher data. Usage: install_studio.sh [studio_dir]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STUDIO="${1:-$HOME/Downes}"

mkdir -p "$STUDIO/courses"
[ -f "$STUDIO/courses/README.md" ] || cp "$REPO/studio/courses-README.md" "$STUDIO/courses/README.md"
cp "$REPO/studio/opencode.json" "$STUDIO/opencode.json"
# The engine's state lands under .downes/xdg — credentials included. The studio
# is a git working tree and the folder teachers share courses from, so the
# ignore rule has to exist before anything can be staged. Appended, not
# overwritten: a teacher's own rules are theirs.
if ! grep -qs '^\.downes/xdg/' "$STUDIO/.gitignore" 2>/dev/null; then
  cat "$REPO/studio/gitignore-template" >> "$STUDIO/.gitignore"
fi
rsync -a "$REPO/studio/.downes/" "$STUDIO/.downes/"   # no --delete: additive
if [ ! -d "$STUDIO/.git" ]; then
  git -C "$STUDIO" init -q
fi
echo "studio ready at $STUDIO"
