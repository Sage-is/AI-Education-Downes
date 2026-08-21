#!/usr/bin/env python3
"""Replay the vault corpus through a hermetic studio. Exit 1 on hard fail."""
import json, os, pathlib, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "harness"))
from assertions import CHECKS, MIN_SLIDE_SEPARATORS

ENV = dict(os.environ, OPENCODE_DISABLE_EXTERNAL_SKILLS="1",
           OPENCODE_DISABLE_CLAUDE_CODE_SKILLS="1")

def run_one(entry):
    # Each run gets its own hermetic studio: isolates provider flakes and
    # makes the "exactly one new course dir" check unambiguous.
    studio = pathlib.Path(tempfile.mkdtemp(prefix="downes-replay-"))
    subprocess.run(["bash", REPO / "scripts/install_studio.sh", studio],
                   check=True, capture_output=True)
    before = {p.name for p in (studio / "courses").iterdir()}
    r = subprocess.run(
        ["opencode", "run", "--pure", "--format", "json", entry["prompt"]],
        cwd=studio, env=ENV, capture_output=True, text=True, timeout=1200)
    new = [p for p in (studio / "courses").iterdir() if p.name not in before]
    errs = []
    if r.returncode != 0: errs.append(f"exit {r.returncode}")
    if len(new) != 1: errs.append(f"{len(new)} new course dirs")
    if entry["skills"] and r.stdout.count('"tool":"skill"') == 0:
        errs.append("skill tool never fired")
    if not new: return errs
    course = new[0]
    if not (course / "00_plan.md").is_file(): errs.append("00_plan.md missing")
    for skill in entry["skills"]:
        fname, pats = CHECKS[skill]
        f = course / fname
        if not f.is_file(): errs.append(f"{fname} missing"); continue
        text = f.read_text(errors="replace")
        errs += [f"{fname}: '{p}' absent" for p in pats if p not in text]
        if skill == "slide-deck" and \
           sum(1 for l in text.splitlines() if l.strip() == "---") < MIN_SLIDE_SEPARATORS:
            errs.append("07_slides.md: too few --- separators")
    for f in course.glob("*.md"):
        if "openai" in f.read_text(errors="replace").lower():
            errs.append(f"{f.name}: 'openai' present")
    return errs

def main():
    full = "--full" in sys.argv
    failed = total = 0
    for line in (REPO / "harness/corpus.jsonl").read_text().splitlines():
        e = json.loads(line)
        if not full and not e["subset"]:
            continue
        total += 1
        errs = run_one(e) or run_one(e)  # one retry on fail (fresh studio each)
        status = "PASS" if not errs else "FAIL"
        failed += bool(errs)
        print(f"{status} {e['run']}" + ("" if not errs else " | " + "; ".join(errs)))
    print(f"\nreplay: {total - failed}/{total} passed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
