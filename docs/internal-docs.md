# Internal docs convention

Some work product is useful to the team and wrong for a public repository.
This repo is public. Two channels exist, and they carry different things.

## The two channels

**Git** carries what a contributor needs to work on the code: architecture,
decisions in neutral language, board cards describing work to be done.

**Backup and sync** carries everything else. Every repo is version-backed-up
and synced independently of git, so the team receives gitignored files in
full. Marking something internal removes it from the public record, not from
the team.

## The split

Internal-only content goes to `docs/dossiers/` — gitignored, never committed:

- Design-review or panel-review narration, in any reviewer voice.
- Opinions attributed to people, whether real, simulated, or composite.
- Draft or unpublished copy: marketing, positioning, pricing, pitch language.
- Unshipped positions, internal disagreement, and anything about a client,
  advisor, or partner that they have not seen.
- The long-form reasoning behind a board card, where the reasoning is useful
  but the framing is internal.

Tracked files may reference that a dossier exists, by date. They must not
restate its findings, name reviewers, or reproduce the argument.

## Persona and simulated reviews

A review conducted in the voice of named people produces text that reads as
quotation but is invention. Published in a repo, it attributes positions to
real people who never held them, in a document bearing our name. This is a
problem independent of confidentiality.

So: persona-driven review output lands in `docs/dossiers/` by default, with no
exception for a first draft. What reaches the board is the work item alone —
project voice, no reviewer, no lens label, no panel framing. Where a card
needs its reasoning, it cites the dossier date and stops there.

## Applying it

- New internal file: write it under `docs/dossiers/`. The folder is already
  ignored; no `.gitignore` edit is needed.
- The ignore rule silently swallows new files there. That is intended, and it
  means such a file never appears in `git status` to remind you it exists.
- Moving an already-committed file here does not remove it from history. If
  content has been pushed, say so plainly rather than treating the move as a
  fix.
- Decisions that change the architecture still get a neutral record under
  `docs/decisions/`.
