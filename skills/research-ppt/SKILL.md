---
name: research-ppt
description: >
  Prepare detailed research-report PPTs from supplied papers, notes, reports and
  experimental results, and review or revise their final artifacts. Use for integrated
  topic reports, paper talks, journal clubs, literature reviews, research progress
  reports and scientific method tutorials. Own evidence, audience prerequisites, narrative,
  style, original figures, production handoff and independent post-production QA;
  delegate actual slide authoring and export to the current ppt-master backend.
license: MIT
metadata:
  version: "0.3.0"
---

# Research PPT

Requires a tool-capable agent with file access, image inspection and code execution;
production also requires ppt-master and a real PPTX renderer.

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
them as proposed assumptions for intake confirmation. Do not ask again for information
already supplied. Repository development and project-structure questions do not start
a presentation intake.

For a research report based on supplied materials, organize the presentation around
the research question or project, integrating relevant sources rather than following
one paper's table of contents or making unrelated paper summaries. A single supplied
file may also support a report; do not require multiple papers. Explicit paper-talk,
review, progress-report and tutorial requests keep their intended scope. Propose
`presentation_type: research_report` and `detail_level: detailed` for new unspecified
briefs, then resolve them through intake. Detail means sufficient explanation and
evidence, with rich notes and backups within the agreed time—not a fixed slide count.

## Load only what the stage needs

| Stage | Reference |
|---|---|
| Requested environment setup | `references/environment-setup.md` |
| Intake, source reading and evidence | `references/preparation.md` |
| Audience, structure, style and figures | `references/story-and-style.md` |
| Backend discovery and production delegation | `references/production-handoff.md` |
| Final render, inspection, revisions and delivery | `references/review-and-revision.md` |

Resolve this skill's absolute directory before using bundled scripts. Runtime
scripts and references live inside this folder. Repository maintenance helpers
are optional; a separately installed current ppt-master is also supported when the
user supplies its path. Do not search unrelated home directories for credentials.

## Durable state and stage gates

Keep each talk in its own **private workspace**. Unless the user specifies a name or
destination, summarize a short project name from the supplied topic/source title and
use `<request-working-directory>/outputs/<project-name>/`. Resolve that working
directory before changing to the skill/backend installation. Pass the name via
`init --name`; the helper makes it a safe filename, preserves Chinese and adds `-02`,
`-03`, etc. for new talks with the same name. Capture the actual path printed by init;
resume an existing talk at its original path. Explicit user names/paths take priority.

Within that workspace:

```text
brief.json                    # requirements, source fingerprints, intake confirmation
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
Default delivery filenames are `exports/<project-name>.pptx`,
`exports/<project-name>.pdf` and `exports/<project-name>-notes.md`, for requested
formats only. Persist them as workspace-relative `output_files` in `brief.json` and
pass them through the handoff. Keep prior revision files and review the exact delivered
PPTX. `outputs/` is private job data, ignored in this repository and never published.

### 0. Agree on the presentation brief

Read the Intake procedure in `references/preparation.md` before evidence preparation.
The helper's `init --name <project-name>` creates the default workspace's `brief.json`;
`--project <private-workspace>` overrides its destination.
`templates/brief.example.json` shows a complete synthetic brief before confirmation.
Extract known requirements and check source availability, then ask only missing or
contradictory essentials in small batches: audience/expertise and purpose, duration
and Q&A, presentation type/depth, language, style/reference intent, structure/focus
and requested deliverables.
Offer concrete choices and explicit delegation where useful. Present a readable brief
that distinguishes supplied requirements, proposed defaults and delegated decisions.

**Gate:** Wait for the user's explicit acceptance before substantive evidence reading,
story design or production, unless an actual prior instruction already authorizes
proceeding with the stated requirements or delegates the necessary choices. Record
that real response/directive and its requirement snapshot in `brief.json`; generic
requests to make a PPT do not grant delegation. For resumed work, reuse the accepted
brief and confirm only material changes. Parent intake does not waive backend gates.

### 1. Prepare the evidence

Inventory relevant supplied papers, reports, notes, result files, figures and existing
slides; expand a supplied folder into explicit file paths for the helper. Read the
selected sources in their exact versions. Notes summarizing another work are navigation,
not verified substitutes for that original; a project report or result log can itself
be a primary source for the user's work. Distinguish published evidence, user results,
author interpretations, presenter analysis and synthetic teaching examples. Map each
claim to its actual sources. Add outside research only when requested or within an
agreed source-gap resolution; keep its attribution separate.

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

For a detailed integrated report, connect background, the research problem, necessary
foundations, methods, results, comparisons, limitations and implications as supported
by the materials. Include the user's progress/next steps only when supplied or clearly
labelled as proposals. Follow `references/story-and-style.md` to record coverage and
place supporting details in notes or true backups without omitting the main argument.

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
route and required gates. Resolve script names, CLI flags, SVG format and template
contract from those instructions. Do not forge its confirmations because our preparation exists.
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
