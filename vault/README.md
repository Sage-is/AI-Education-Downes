# vault/

This directory is user data. The agent writes one folder here per run.
Every artifact is Markdown so you can read it without special tools.

## Run folders

`Vault.create_run_dir()` in `src/downes/utils/vault.py` names each run:

```
vault/<YYYYMMDD_HHMMSS>_<prompt-slug>
```

The timestamp comes from the run start. The slug is your initial prompt, passed through `sanitize_for_filename()`: it drops `\ / * ? : " < > |`, collapses whitespace to single hyphens, lowercases everything, and truncates at 50 characters. Other characters — parentheses, apostrophes, dots — survive untouched:

```
20260311_081542_given-the-topics-of-sage.education-and-sage.is-ai-
20251213_192322_let's-craft-a-3-video-course-on-board-game-art-des
```

## Step folders

Each plan step gets its own folder inside the run, named by the same sanitizer applied to the step name:

```
00_planning/
01_search-for-sage.education-and-sage.is-platform-/
02_fetch-and-verify-top-3-results-from-sage.educat/
99_summary/
llm_transcripts/          # when LLM call recording is on
```

Inside a step folder, the first artifact takes the step name as its
filename (`01_search-for-....md`). Later artifacts use the sanitized
artifact name plus an incrementing counter:

```
02_searx_search_1.md
03_verify_and_summarize_1.md
04_verify_and_summarize_1.md
```

Strings are written verbatim. Any other content lands in a fenced
` ```json ` or ` ```text ` block inside the `.md` file.

## 00_planning and 99_summary

- `00_planning/` — the task list the agent built before doing any work.
  Start here to see what the run intended. Current runs name it
  `00_planning.md`; older runs use `task_list_1.md`, plus
  `task_list_revision_N_1.md` when you revised the plan mid-run.
- `99_summary/` — the final answer produced by the last step. Read this for the finished product. Current runs name it `99_summary.md`; older runs use `final_answer_1.md`.

Everything between them is intermediate work: search results, page
extracts, verification notes.

## Reading a run start to finish

1. Open the run folder whose timestamp and slug match your query.
2. Read `00_planning/00_planning.md` for the plan.
3. Walk the numbered step folders in order. Each step's same-named file holds that step's output; the counter-suffixed files hold individual tool calls within it.
4. Read `99_summary/99_summary.md` for the result.
5. If something looks wrong, check `llm_transcripts/` for the raw
   prompts and responses behind each call.

## Obsidian, sync, sharing

- **Obsidian:** open this repo folder as a vault (File → Open vault).
  Every run becomes a browsable note tree with working wiki-style links.
- **Sync:** the folders are plain files. Dropbox, iCloud, Syncthing, or
  git-on-a-private-remote all work.
- **Sharing a run:** zip or copy the run folder. It has no dependencies
  outside itself — any colleague can read it in any editor.

## What git tracks

`.gitignore` contains:

```
vault/*
!vault/README.md
```

Only this README is tracked. Every run folder is ignored.

## Warning: `make things_clean`

The Makefile's `things_clean` target runs `git clean -Xdf`, which
deletes every gitignored file in the repo — including every run in this directory. This README survives only because git tracks it. Copy any run worth keeping somewhere outside `vault/` before you run it.
