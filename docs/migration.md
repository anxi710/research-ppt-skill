# Migration from the private ResearchDeck prototype

This release changes the ownership boundary, rather than just renaming the old package.

| Previous prototype | General skill |
|---|---|
| Historic ppt-master component adapter | Current upstream submodule; no copied exporter |
| Case-specific build_deck.py as starter | Backend-owned production from a versioned handoff |
| Personal/institution-specific defaults | Explicit audience and optional neutral style profiles |
| Private accepted deck and original figures | Excluded; only synthetic fixtures are public |
| End-to-end responsibility in one build layer | Preparation → delegation → independent review |
| Export-centric completion | Evidence/visual/artifact acceptance with targeted revision |

Retained practices: source-first reading, figure-first page jobs, audience prerequisites,
short on-slide text, useful notes, crop provenance, hidden-backup checks and hash-bound QA.

The old private archive remains separate. Its original paper, logo, template, slides,
source imagery and fixed-version adapter are not required to run this repository and
must not be added to its public history.
