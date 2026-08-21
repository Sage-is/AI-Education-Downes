#!/usr/bin/env python3
"""Validate corpus/ against manifest.json. Stdlib only; exit 1 on any failure.

Naming contract ported from src/downes/utils/vault.py sanitize_for_filename:
run dirs are <YYYYMMDD_HHMMSS>_<slug>, slug lowercase, no [\\/*?:"<>|],
whitespace collapsed to single hyphens, max 50 chars.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUN_DIR_RE = re.compile(r'^\d{8}_\d{6}_[^\\/*?:"<>|A-Z\s]{1,50}$')

def main() -> int:
    manifest = json.loads((REPO / "corpus" / "manifest.json").read_text())
    errors = []
    for entry in manifest:
        name = entry["run"]
        run = REPO / "corpus" / "runs" / name
        exp = entry["expected"]
        if not RUN_DIR_RE.match(name):
            errors.append(f"{name}: dir name violates vault naming contract")
        if not run.is_dir():
            errors.append(f"{name}: missing from corpus/runs/")
            continue
        step_dirs = sorted(p.name for p in run.iterdir() if p.is_dir())
        if step_dirs != exp["step_dirs"]:
            errors.append(f"{name}: step dirs drifted: {step_dirs}")
        if exp["has_planning"] and not (run / "00_planning").is_dir():
            errors.append(f"{name}: 00_planning missing")
        if exp["has_summary"] and not (run / "99_summary").is_dir():
            errors.append(f"{name}: 99_summary missing")
        count = sum(1 for p in run.rglob("*") if p.is_file())
        if count != exp["file_count"]:
            errors.append(f"{name}: file count {count} != {exp['file_count']}")
    for e in errors:
        print(f"FAIL: {e}")
    print(f"corpus: {len(manifest)} runs, {len(errors)} failures")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
