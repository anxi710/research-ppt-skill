# Validation status

The generic helper layer is tested locally with synthetic inputs. These checks are
separate from backend production, remote publication and a real presentation's acceptance.

## Current helper checks

Using the selected conda `docs` environment,
`python -m unittest discover -s tests -v` completed **44 tests**: **43 passed** and
the opt-in real-renderer test was skipped. `python scripts/check_repo.py` and the
skill frontmatter validator also passed.

The tests cover proposed presentation type/depth, explicit overrides, stale depth
acceptance, unchanged legacy briefs and mixed-material synthesis provenance through
handoff, as well as request-directory output defaults, Unicode project names, collision
preservation, explicit path overrides, named delivery handoffs, invalid inputs leaving
no default workspace, pending or stale intake records, explicit delegation, Q&A reservations,
source/contract mutation invalidation, missing evidence/style/assets, immutable handoffs,
pending reviews, missing backup-slide review coverage, stale backend receipts, unrelated
reviewed images, source crop geometry, notes/hidden flags, and Git-bundle recovery without
overwriting working files. Recovery coverage does not make it a normal clone setup step.

Fictional intake records in synthetic tests/examples illustrate the contract; fabricated
final-deck review records exist only inside unit tests. Neither represents actual user
approval, visual review or scientific validation.

A separate preparation-only synthetic trial used a reference report, a pilot-result
CSV and an interpretive note. It produced an integrated plan with source-qualified
comparisons, explicit gaps, notes and hidden backups. The deliberately short materials
supported a 900-second main plan against a requested 1500-second speaking budget;
preflight failed on timing and production remained blocked. The trial did not fill the
gap with invented findings, shorten the accepted budget or claim a finished deck.
This is evidence about that preparation scenario, not end-to-end PPTX generation.

## Optional real-renderer coverage

Enable `RUN_RENDER_TESTS=1` with LibreOffice to render a two-slide synthetic deck with
one hidden backup. The test checks both all-slide and visible-only output and confirms
that the source PPTX bytes are unchanged.

An earlier recorded run of this test suite completed **23 tests**, including that renderer
test, with zero failures or skips. The current default run above did not repeat rendering;
the earlier result is historical evidence, not a render of a current real presentation.

## Outside these checks

- End-to-end slide production with the current ppt-master implementation.
- Upstream Git clone/update over the network.
- Authenticated remote repository creation or push.
- Hosted GitHub Actions and Dependabot execution.
- A real-paper end-to-end presentation using this skill.

The configured upstream branch, recorded gitlink and license observations document
backend provenance. They do not certify current production compatibility; a new job still
reads the actual checkout's instructions and validates representative pages.

Run the local tests again in the target environment. If a real renderer is unavailable,
the renderer test is skipped unless explicitly enabled; do not describe a skipped test as
passed. A real deck still requires source reading and visual/semantic review.
