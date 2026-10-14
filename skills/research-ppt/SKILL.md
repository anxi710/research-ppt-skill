---
name: research-ppt
description: >
  Prepare evidence-grounded research presentations and review or revise their final
  PPTX artifacts. Use for paper talks, journal clubs, literature reviews, research
  progress reports, scientific method tutorials, or slide-deck requests based on
  research sources. Own source preparation, audience prerequisites, narrative,
  style, original figures, production handoff and independent post-production QA;
  delegate actual slide authoring and export to the current ppt-master backend.
license: MIT
compatibility: Requires a tool-capable agent with file access, image inspection and code execution; ppt-master and a real PPTX renderer for production.
metadata:
  version: "0.2.0"
---

# Research PPT

## Mission and boundaries

Deliver an accurate, teachable, visually coherent research talk—not only an outline.
Own everything **before and after production**. ppt-master is the default production
backend, not this skill's parent instruction system or a version-frozen exporter.
Do not author a second production engine here. Backend expertise may refine page
composition; source claims, target audience, figure identity, and accepted scope are
not silently changed to make a layout easier.

User requirements determine language, duration, structure, medium and style. Never
hard-code an institution, brand, presenter, research topic, 21-page count or 27-minute
length. Select defaults only for genuinely unspecified, low-risk choices and record
them as assumptions. Do not ask again for information already supplied.

## Load only what the stage needs

| Stage | Reference |
|---|---|
| Intake, source reading and evidence | `references/preparation.md` |
| Audience, structure, style and figures | `references/story-and-style.md` |
| Backend discovery and production delegation | `references/production-handoff.md` |
| Final render, inspection, revisions and delivery | `references/review-and-revision.md` |

Resolve this skill's absolute directory before using bundled scripts. Runtime
scripts and references live inside this folder. Repository maintenance helpers
are optional; a separately installed current ppt-master is also supported when the
user supplies its path. Do not search unrelated home directories for credentials.

## Durable state and stage gates

Keep each talk in its own **private workspace**, normally outside this repository:

```text
brief.json                    # goals, audience, time, language, source fingerprints
analysis/evidence.json        # claims, source locators, conditions, uncertainty
analysis/figure_manifest.json # assets and their original-source provenance
analysis/backend.json         # actual backend path/revision, not a version constraint
design/style_profile.json     # design decisions and their reference/assumption basis
design/slide_plan.json        # page jobs, core visuals, reading order and speaker notes
handoff/run-*/                # immutable preparation snapshot and production brief
production/                  # backend-owned workspace; do not impose its schema
qa/                          # machine audit, real renders, page reviews and issues
exports/                     # accepted PPTX/PDF/notes and provenance
state.json                    # stage, accepted artifacts, unresolved issues
```

Restore from these files before resuming. Never infer completion from a previous
assistant message or a successful export alone. Do not overwrite accepted inputs,
previous snapshots, earlier QA or final versions.

### 1. Prepare the evidence

Read supplied sources in their exact versions. Reports and summaries are navigation,
not replacements for the source. For multiple papers, record which paper supports
which claim; separate paper claims, author interpretations, presenter analysis and
explicitly synthetic teaching examples. Add outside research only when requested
or needed to resolve a declared source gap, with separate attribution.

Inspect original figure/table images, not just parsed text. Record definitions,
units, axes, denominators, confidence intervals, intervention/control, sample size,
compute budget, and the actual unit of a step/decision where relevant. Register
contradictions; do not silently repair or reconcile them using background knowledge.

**Gate:** Every load-bearing factual claim has an exact source locator and its scope;
no unresolved contradiction is hidden behind an unconditional slide title.

### 2. Design the talk and style

Identify the central question and a small set of justified takeaways. Work backward
from the audience's missing prerequisites. Teach only what is necessary to understand
the key method and evidence. An empirical diagnostic paper need not pretend to have
a new algorithm; a theory paper may center on an equation or counterexample rather
than a chart. Literature reviews require synthesis, not a paper-by-paper dump.

Each page has one question, one topic, one core visual or coherent panel group,
source IDs, reading order, minimal display text, a scoped takeaway, speaker notes,
planned duration and visible/backup status. Separate design from result when needed.

Extract visual rules from a reference deck—not its old names, dates, claims or logos
without permission. Record palette, fonts, aspect ratio, source footer, visual density
and layout variations in a style profile. Never use decorative filler to eliminate
whitespace. Enlarge/recompose the core visual first; preserve useful margins.

Prepare high-resolution original figures. Preserve axes, legends, ticks, units,
panel labels and uncertainty information. Split panels only when the relevant legend
and context remain attached. Original data plots must not be redrawn or generatively
repaired. Native explanatory diagrams are allowed, clearly distinguished from evidence.

**Gate:** Sources and assets are available and checked; the talk has an audience-fit
story and time budget; every page has a real job and planned core visual.

### 3. Delegate production to current ppt-master

Resolve a real checkout. At the beginning of a new job, update the configured branch
when network access and user scope permit. Record failures accurately; never call an
unfetched checkout "latest". Record the actual revision for this job and do not update
it midway through construction/review. Refreshing a backend is not a reason to refresh
the paper version or its historical results.

Read the backend's current `AGENTS.md` and skill entry, follow its current documented
route and required gates. Do not assume historical script names, CLI flags, SVG format,
or template contract. Do not forge its confirmations because our preparation exists.
Pass our brief as source material and constraints, not as its internal design lock.
Do not disable attribution, integrity, licensing or safety checks.

Create an immutable handoff with preparation files and checksums, source/asset paths,
page requirements, notes and acceptance criteria. The backend should try representative
method, dense-experiment and explanation pages before expanding. Obtain a build receipt:
actual command/path/revision, output paths, source locations and limitations.

**Gate:** A real PPTX exists and the receipt accurately states what was used. Export
success is not final acceptance.

### 4. Independently inspect the produced deck

Audit structural integrity, notes, hidden-slide flags and correspondence to the plan.
Then render the **actual final PPTX**, including hidden backups, using a real PPTX
renderer. SVG previews alone do not validate PPTX import/export or font substitution.
Inspect the montage, every full slide and necessary figure crops at useful magnification.

Check scientific claims/numbers/units/conditions against source evidence; inspect axes,
legends, typography, editable text, clipping, stretching, visual density, source footers,
notes, speaker timing and audience comprehension. Backend self-checks do not replace
this independent comparison to the preparation contract.

Record defects with slide ID, category, evidence or screenshot, severity, requested
change and acceptance test. Pending/unviewed pages cannot be marked passed. Hashes
bind records to artifacts but cannot certify that the reviewer understood the science.

### 5. Repair at the correct layer and rerender

For a factual/source issue, repair the evidence/plan and create a new handoff. For a
visual/export issue, send a targeted request to ppt-master, preserving correct content
and accepted style. If a figure is illegible, enlarge/split/recrop with context; do not
shrink all fonts. If repeated local fixes fail, simplify the page structure or report
the unresolved limitation. Never declare success just because retry budget was used.

Regenerate, render, inspect affected pages and check whole-deck consistency. The final
review must correspond to the final PPTX and latest contract. A changed file invalidates
its old approval. Do not rewrite old hashes to pretend an old review was performed anew.

### 6. Deliver and learn

Deliver the requested artifacts (normally PPTX, visible-slide PDF, speaker notes and
source/provenance package). Verify that every path exists. Describe editable vs raster
content honestly; paper images are not editable source-data charts. Timing is a plan,
not a measured rehearsal. Missing render support means an explicitly unvalidated draft.

Do not publish papers, private templates, logos, fonts or unpublished results merely
because this skill is MIT. Extract only generalized, non-identifying lessons for future
skill improvements; add synthetic regression fixtures rather than private decks.

## Helper tools

`python scripts/workflow.py --help` initializes the workspace, validates preparation,
creates handoffs, seeds **pending** reviews and checks final gates.
`python scripts/decktools.py --help` supplies optional material/render/audit helpers.
These are deterministic preparation and verification tools—not an autonomous
scientific judge or a replacement for ppt-master production.
