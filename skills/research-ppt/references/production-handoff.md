# Production delegation contract

## Ownership

Research PPT Skill owns evidence and communication decisions, prepared assets, acceptance
criteria and independent review. ppt-master owns its internal routing, specifications,
layout implementation, native object generation and export. Reuse its full current
capabilities; do not copy a historic exporter or maintain a competing PPT builder.

ppt-master may also contain planning/verification capabilities. Our preparation is an
input brief, not a substitute for its mandatory runtime gates. Reconcile overlapping
planning by mapping our audience/claims/assets into its current schema; never impersonate
user confirmation or manufacture a backend lock. Report genuine conflicts to the user.

## Discover current backend

The repository helper `scripts/upstream.py update` updates the configured branch for a
new job. It is maintenance, not a production command. A standalone installation may
instead be supplied as an explicit absolute path. Do not infer a usable local directory
from a public URL or from a previous session.

Read the actual current backend entry instructions and the route they select. Execute
only documented commands for that revision. Record path, revision, dirty state, remote,
license observation and read-document hashes in `analysis/backend.json` or the build receipt.
A successful document probe is not a successful generation. No network or update failure
may be reported as "latest". Do not bypass upstream integrity or attribution checks.

Use a current revision for each new job; keep that run stable until review finishes. A
recorded SHA is provenance, not an exact-version requirement in this skill. Existing jobs
can reproduce their original revision; deliberate upgrades create a new build/review.

## Handoff

Run preparation preflight. Create `handoff/run-*/` containing snapshots of:

1. brief, evidence, figure inventory, style profile and page plan;
2. file fingerprints and references to source/asset files in the private workspace;
3. a production brief describing requirements, editable/raster distinction and acceptance;
4. a pending receipt template for the backend to fill after actual production.

The agent must provide this handoff to the backend. The files are not automatically sent
to an API; the helper performs no model calls. Source/asset paths remain local, and work
happens under `production/`, not inside the upstream submodule.

## Requested output

A real PPTX with native editable text/annotations when requested, original source figures,
notes on each page, and genuine hidden flags for backups. Return build inputs/source paths,
commands actually run, backend identity, exported paths, source hashes and known limits.
Do not convert entire slides into background screenshots and call the result editable.

Inspect representative pages before expanding the deck, within the backend's allowed
workflow. A page-count/claim/figure change is a contract change, not a silent design tweak.
Send it back to the orchestrator, update the plan, then take a fresh handoff snapshot.

## Revision requests

Each issue contains `id`, `slide_id`, `category`, `severity`, evidence/screenshot, requested
change and acceptance criteria. Cosmetic fixes preserve evidence, numeric labels, figure
identity and unaffected slides. Evidence corrections update the preparation snapshot first.
The backend's repair receipt states which slides changed, what remains unresolved, and
where the new artifact exists. The orchestrator rerenders and rechecks it independently.
