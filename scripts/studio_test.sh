#!/usr/bin/env bash
# The scriptable one-line test: fresh hermetic studio, canonical prompt,
# CP0 green checks. Exit nonzero on any failure.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STUDIO="$(mktemp -d /tmp/downes-studio-test.XXXXXX)"
export OPENCODE_DISABLE_EXTERNAL_SKILLS=1 OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1

bash "$REPO/scripts/install_studio.sh" "$STUDIO" >/dev/null
cd "$STUDIO"

EVENTS="$STUDIO/events.json"
opencode run --pure --format json \
  "Generate 3 measurable learning objectives for Grade 9 Intro to Art" \
  > "$EVENTS"

COURSE=$(find courses -maxdepth 1 -mindepth 1 -type d ! -name probe | head -1)
fail() { echo "FAIL: $1"; exit 1; }

[ -n "$COURSE" ] || fail "no course folder created"
[ -f "$COURSE/00_plan.md" ] || fail "00_plan.md missing"
[ -f "$COURSE/01_objectives.md" ] || fail "01_objectives.md missing"
grep -q "## Learning Objectives" "$COURSE/01_objectives.md" || fail "objectives header absent"
grep -q "### Objectives" "$COURSE/01_objectives.md" || fail "objectives list header absent"
grep -q '"tool":"skill"' "$EVENTS" || fail "skill tool never fired"
if grep -qi openai "$EVENTS" "$COURSE"/*.md; then fail "'openai' visible"; fi

echo "OK: one-line test green ($COURSE)"
