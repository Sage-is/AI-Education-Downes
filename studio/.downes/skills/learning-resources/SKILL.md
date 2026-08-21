---
name: learning-resources
description: Curate learning resources (articles, videos, OER, datasets) for a course topic, grounded in real search results. Use when the user asks for resources, materials, readings, or links, or when a course plan names 06_resources.md.
---

# Curating learning resources

## Inputs to gather (ask if missing)

- topic (required) · audience (required) · max_items (default: 8)
- resource_types (default: article, video, dataset, toolkit)

## Mode A — grounded (default)

Run websearch FIRST — this mode is forbidden without it. Scope queries to
vetted education sources with site: filters; prefer, in order:

- OER: oercommons.org, openstax.org, ck12.org, oer.commons
- Standards + practice: iste.org, teachengineering.org, pbslearningmedia.org
- Reference: en.wikipedia.org, khanacademy.org, edutopia.org
- Primary sources and official docs for the topic's own tools

Record every query and its returned results verbatim in `90_research.md`
per the method. Then act as an educational librarian on those REAL hits:
keep every URL exactly as returned — never invent or modify URLs; titles
may be lightly rephrased for clarity; type is a short label (article,
video, dataset, repository, toolkit); summary is one sentence; suggested
use says how an educator might apply it.

## Mode B — offline (only when search is unavailable)

Name well-known sources WITHOUT URLs — a named book, a named organization,
a named openly-available course. Mark every entry [Unverified]. Never
fabricate a URL, a publication date, or a [Verified] tag; a resource list
with invented links is worse than a short honest one. The research log
must carry the no-search line per the method.

## Output contract

Write `06_resources.md` in the current course folder. The file must contain
only, in this order:

```markdown
## Synthesized Learning Resources

1. **<Title>** — [Unverified]
   - Type: <type>
   - URL: <verbatim URL, Mode A only>
   - Summary: <one sentence>
   - Suggested use: <one sentence>
```

One numbered entry per resource, up to max_items. Every entry carries a
`Type:` line. Every URL present must also appear in `90_research.md`.

