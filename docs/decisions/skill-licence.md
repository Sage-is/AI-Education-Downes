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
- The split is clean **at the repo level**: `AI-Education-Downes` (AGPL,
  curriculum home) · `ai-ui-mini` (MIT, platform).

## Where the split stopped being clean — unresolved

It is no longer true that the launcher travels only with the curriculum repo.
`scripts/package_macos.sh` stages `launcher/downes.sh`, `launcher/downes.sb`
and `scripts/install_studio.sh` into **both** payloads; only the curriculum
template is guarded by `if [ "$PRODUCT" = "downes" ]`. Those files live in this
AGPL repo and carry no per-file licence header.

So the shipped `mini` tarball mixes AGPL launcher files with the MIT engine and
app, while `packaging/homebrew/mini.rb` declares `license "MIT"` and the asset
is published from the MIT repo. By this project's own rule — AGPL wins when
mixed, and combined artifacts ship AGPL from the AGPL repo — two of those three
facts are wrong.

This shipped in v0.1.2 and again in v0.1.3. **It needs a decision, not a
patch.** The options, none of them yet chosen:

1. Put an explicit MIT (or dual) header on `launcher/downes.sh`,
   `launcher/downes.sb` and `scripts/install_studio.sh`, making `mini`'s
   `license "MIT"` true. Cheapest, and keeps mini genuinely MIT.
2. Relicense `mini.rb` to AGPL and publish its asset from this repo. Honest,
   but contradicts "mini is the MIT platform" as a positioning claim.
3. Give mini its own MIT launcher so the payloads share no AGPL file. Most
   work; removes the question permanently.

## Open sub-question for the advisor

Whether teachers redistributing generated course folders need an explicit
dual-licence grant on the *outputs* (as opposed to the skills). Course
outputs are the teacher's work product; the recommendation is that generated
courses carry no Downes licence obligation — the teacher owns them. Confirm
before launch.
