# Decision: licence for the curriculum skills

Status: **RECOMMENDED — pending advisor ratification** (TODO.md #interview card)

## Recommendation

The eight curriculum skills and the studio config **ship AGPL-3.0**, matching
this repo. The platform fork `ai-ui-mini` stays **MIT** (upstream opencode's
licence, kept upstreamable). The two licences live in two repos and never mix
in one file.

## Why

- The skills are this repo's real asset and its identity; AGPL keeps
  classroom redistribution copyleft, so improved skills flow back.
- The fork is a light branding layer over MIT code; keeping it MIT means our
  patches can be offered upstream and the rebase tax stays low.
- The split is clean: `AI-Education-Downes` (AGPL, curriculum home) ·
  `ai-ui-mini` (MIT, platform) · launcher + studio config travel with the
  curriculum repo under AGPL.

## Open sub-question for the advisor

Whether teachers redistributing generated course folders need an explicit
dual-licence grant on the *outputs* (as opposed to the skills). Course
outputs are the teacher's work product; the recommendation is that generated
courses carry no Downes licence obligation — the teacher owns them. Confirm
before launch.
