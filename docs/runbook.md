# Runbook

For first-time use and later maintenance, start with the [usage guide](usage.md)
([中文](usage.zh-CN.md)). To ask an agent to configure the software environment,
use the [environment setup instructions](../skills/research-ppt/references/environment-setup.md).
This runbook supplies the detailed material-processing and acceptance commands.

The commands below are deterministic helpers for an agent. They do not read research
materials semantically, choose a narrative, judge visual correctness, or produce the
presentation autonomously. The agent integrates supplied papers, notes, experimental
results, data, figures and reports around the research topic/question; explicit
single-paper talks remain supported.

Use Python 3.11 and a current tool-capable host. Before changing directories, capture
the absolute working directory of the user's request and resolve relative skill-entry
and material paths against it. Locate the real skill and scripts, then use their
resolved absolute paths internally. Default outputs belong under the captured request
directory, rather than the skill's install location. Run `init` in the request
directory with the resolved script path, or use an absolute `--project` beneath the
captured request directory after changing directories, with resolved material paths.
Absolute entry and material paths remain valid when running elsewhere. The examples
below treat this repository's root as the request directory and use its ignored
`./outputs/`.

Obtain the repository with its backend submodule, then run the commands below from
the checkout root:

```bash
git clone --recurse-submodules <repository-url> research-ppt-skill
cd research-ppt-skill
```

Replace `<path-to-material>` below with the actual material folder's absolute or
relative path. Replace other angle-bracket placeholders with real values before
running commands; retain quotes around paths containing spaces.

## 1. Confirm requirements and initialize a workspace

Start a new presentation with the parent's intake procedure in
`./skills/research-ppt/references/preparation.md`. Reuse requirements already supplied;
ask short batches only for missing or contradictory essentials: research topic/question,
audience and prior knowledge, purpose, presentation type and depth, duration and whether
it includes Q&A, language, style/template, structure/focus and deliverables. Source
availability checks and template previews may support this conversation; substantive evidence preparation and story design wait for
acceptance. Repository development and project-structure questions do not start intake.

Once the core command values are available, summarize a short descriptive project
name from the topic or supplied source title. This naming step does not require
substantive evidence reading and must not introduce unsupported research claims.
Use a safe single path component and preserve Chinese when present. Initialize:

```bash
python -m pip install -r requirements.txt
python scripts/upstream.py update --out outputs/backend-observation.local.json
python ./skills/research-ppt/scripts/workflow.py init \
  --name synthetic-research-report \
  --source "<path-to-material>/paper-a.pdf" \
  --source "<path-to-material>/paper-b.pdf" \
  --source "<path-to-material>/reading-notes.md" \
  --source "<path-to-material>/experiment-results.csv" \
  --template "<path-to-template>.pptx" \
  --presentation-type research_report --detail-level detailed \
  --minutes 27 --language zh-CN \
  --audience "AI researchers outside this subfield"
```

Omit `--template` without a reference. A user may supply a material folder, but
`init --source` requires individual existing files, not a directory. The agent
inventories the folder, selects relevant readable files and repeats `--source` for
each one, using the appropriate readers for its format. Initialization copies and
fingerprints inputs; it does not classify content, synthesize findings or process
folder structure semantically.

Without `--project`, the command creates `./outputs/<safe-project-name>/brief.json`
relative to its working directory and prints the actual workspace path. For example,
running from `/work/research-ppt-skill` creates
`/work/research-ppt-skill/outputs/synthetic-research-report/brief.json`. Later commands
must use the actual path printed by `init`; replace the example paths below when
needed. For a new same-name project, the helper adds `-02`, `-03`, and so on; it
never overwrites or implicitly resumes an existing talk. To resume, explicitly
identify the original workspace and reuse its records without running `init`.
Preserve existing workspace and `output_files` paths rather than rewriting them
solely to adopt new naming defaults.

Explicit `--project` overrides the directory and must point to a new, empty
workspace; relative paths resolve from the invocation directory. Explicit filenames
also take priority. The agent supplies `--name`; if omitted, the helper falls back
to the source filename stem without semantically summarizing it. The agent normally
maintains `brief.json` from the conversation; the user need not write JSON first.

Working artifacts stay in the workspace. Accepted exports default to
`exports/synthetic-research-report.pptx`, `exports/synthetic-research-report-preview.pdf` and
`exports/synthetic-research-report-notes.md`, for requested formats only. Keep all task
materials private and out of commits/publication, including the ignored `outputs/`.

See the complete, pending [brief example](../skills/research-ppt/templates/brief.example.json).
It uses a synthetic teaching source and reserves 5 minutes of a 25-minute session for
Q&A, leaving 20 minutes for visible slides. Its fingerprint belongs to the synthetic
fixture generated by `examples/synthetic/prepare.py`. For a real talk, keep the source
inventory and hashes generated by `init` for the supplied files; use the example to
understand the fields rather than replacing that inventory.

| Brief field | What to enter |
|---|---|
| `project_name` | Optional short descriptive name for output defaults; use a safe single path component, preserving Chinese. It does not grant intake consent. |
| `output_files` | Optional workspace-relative paths under `exports/`, keyed by requested `pptx`, `pdf`, and/or `speaker_notes`; for example, `{"pptx": "exports/synthetic-research-report.pptx"}`. User filenames take priority. These are output defaults, not intake consent. |
| `presentation_type` | New `init` proposal: `research_report`; alternatives: `paper_talk`, `literature_review`, `progress_report`, `method_tutorial`. Set with `--presentation-type` or edit the brief before intake. |
| `detail_level` | New `init` proposal: `detailed`; alternatives: `standard`, `overview`. Set with `--detail-level` or edit the brief before intake. |
| `audience`, `purpose` | Prior knowledge and what the audience should learn, discuss or decide. |
| `target_minutes` | The agreed time budget; interpret it together with `qa_time_included`. |
| `qa_time_included`, `qa_minutes` | Whether Q&A uses that budget; reserve a positive amount smaller than the total when included, otherwise use zero. |
| `language` | The requested language; describe separate slide/delivery languages when needed. |
| `style_intent` | Agreed tone, density and template-use intent; detailed visual decisions go in `design/style_profile.json`. |
| `sections` | Required sections in order; an empty list allows the agent to propose a structure from the sources. |
| `deliverables` | Requested outputs, such as `pptx`, `pdf`, `speaker_notes`. |
| `sources` | Local copies and fingerprints created by `init`; record exact versions and appropriate roles for each supplied file. |
| `assumptions`, `research_connection` | Explicit assumptions and any requested connection to the user's research. |
| `intake_confirmation` | Pending by default; `intake` fills the snapshot, and the agent records only an actual acceptance or delegation. |

Inputs are copied into the private workspace and fingerprinted. Ordinary inputs
initially have `role: research_source`; `--template` creates a `style_reference`.
After initialization, the agent sets each source's metadata role as appropriate:

| Source role | Use |
|---|---|
| `research_source` | Papers and other research sources supporting attributed claims. |
| `reading_note` | Supplied notes or summaries; navigation and interpretation with their own provenance. |
| `user_result` | The user's experimental results, data, figures or progress records. |
| `background_reference` | Supplied background or prerequisite material. |
| `style_reference` | Layout/style guidance, not scientific evidence. |

Retain generated source IDs, copied paths and SHA-256 hashes; changing a role does
not change the file's fingerprint. The script does not infer these roles from content.
Do not treat a reading note as the missing original paper or a style reference as
research evidence. Preserve the original file inventory rather than inserting example
source records.

Update the exact source version, purpose, sections, Q&A policy/reserved minutes, style
intent, deliverables and explicit assumptions in `brief.json`. New report type/depth
values are proposals to confirm, not accepted requirements. When present,
`presentation_type` and `detail_level` are included in intake snapshots; legacy briefs
without them remain valid and must not be silently rewritten on resume.

Set `qa_minutes` to the included Q&A reservation, or zero when Q&A is outside the budget. Visible-slide time is `target_minutes` minus
that reservation. Initialization leaves Q&A unspecified and intake pending; its defaults
are proposals, not user approval. Then prepare the requirement snapshot:

```bash
python ./skills/research-ppt/scripts/workflow.py intake --project outputs/synthetic-research-report
```

`intake` validates the brief and writes a **pending** `intake_confirmation` snapshot
(an unchanged, already accepted snapshot is preserved).
Present a readable summary of supplied requirements, proposed defaults and delegated
decisions. Wait for the user's acceptance unless a prior actual instruction already
authorizes this brief or explicitly delegates the relevant choices. A generic request to
make a PPT is not delegation; an instruction such as "use these requirements and start"
can authorize proceeding without another confirmation round.

Only after that actual response/directive, record `status: confirmed` or `delegated`
and the real user message quote or retrievable reference in `user_response`, retaining
the generated `requirements` snapshot. There is no CLI approval flag: the script neither
asks the user nor supplies consent. A recorded quote/reference is metadata; the agent
must ensure it reflects a real instruction. `preflight` and `handoff` reject a missing, pending
or stale confirmation. For resumed work, reuse the accepted brief; reconfirm material
changes to the captured requirements or source identities/content/roles. Updating source
version labels or internal assumptions alone does not invalidate the snapshot.

An initialized workspace deliberately fails preflight until intake and evidence/style/plan
are ready. Parent confirmation does not waive any current ppt-master confirmation gate.

`upstream.py update` requires Git/network access and a real gitlink. It follows the current
configured branch, does not discard dirty changes and does not execute upstream code.
Record its output, then read the current backend entry instructions before production.

## 2. Read sources and inspect style

```bash
python ./skills/research-ppt/scripts/decktools.py extract-pdf \
  --pdf outputs/synthetic-research-report/inputs/source_01.pdf --out outputs/synthetic-research-report/analysis/paper.md
python ./skills/research-ppt/scripts/decktools.py render-pdf \
  --pdf outputs/synthetic-research-report/inputs/source_01.pdf --pages 1-5 \
  --out outputs/synthetic-research-report/qa/source-pages --dpi 160
python ./skills/research-ppt/scripts/decktools.py inspect-template \
  --pptx outputs/synthetic-research-report/inputs/template.pptx --out outputs/synthetic-research-report/analysis/template
```

Read exact definitions, main results and necessary supplements. For supplied notes,
reports, data and figures, use appropriate readers and retain their conditions,
versions and provenance. Open page images for figures/tables. Render the reference
PPTX when present; statistics alone miss theme inheritance and image content. The
PDF helper avoids OCR and uses PDFium for rendering.

Organize the evidence around the research question, not file order. Distinguish
published findings, the user's results, interpretations and presenter analysis;
trace comparisons to their contributing sources and check whether conditions permit
them. Label missing evidence, conflicting findings and preliminary results. Follow
the supplied materials: do not invent results or expand research automatically.
For agreed background or benchmark concepts, the agent seeks useful images from
original papers or official project/task documentation even when the supplied paper
has none, unless sources or browsing are explicitly restricted. Record these as
attributed external context with exact versions and original images; this does not
authorize new scientific claims or a broader literature search.

## 3. Prepare original figures

For supplied image files, register their copied originals, source IDs, hashes and
verified assets directly; they do not need a PDF crop. For new plots calculated
from supplied data, retain the dataset, computation, conditions and exclusions,
and label the plot as analysis rather than as an original published figure.

For PDF figures, populate `analysis/figure_manifest.json` from actual inspected regions. Coordinates
are top-left-origin PDF points on an unrotated page; do not paste screenshot pixels.
The crop helper accepts one PDF at a time; for multiple sources, pass a source-filtered
crop manifest and merge the verified records into the workspace's figure inventory.

```bash
python ./skills/research-ppt/scripts/decktools.py crop \
  --pdf outputs/synthetic-research-report/inputs/source_01.pdf \
  --manifest outputs/synthetic-research-report/analysis/figure_manifest.json \
  --out outputs/synthetic-research-report/assets/paper --dpi 360
python ./skills/research-ppt/scripts/decktools.py montage \
  --images outputs/synthetic-research-report/assets/paper --out outputs/synthetic-research-report/qa/figure-montage.png
```

The crop report records dimensions, hashes and **pending** review. Inspect each figure,
then enter its `path`, `sha256`, `review_status: verified` and review observations in the
figure manifest. Do not change pending status before actually checking axes/legends.
Unusual page boxes, rotation and user units may require a separately normalized PDF and
new provenance. Verify a known geometry region before bulk cropping such documents.

For optional generated concept illustrations, see the [image generation setup guide](../skills/research-ppt/references/image-generation.md) for Codex, Claude Code and direct API use. Keep generated illustrations distinct from source evidence and review their scientific meaning and style before production.

## 4. Plan, preflight and handoff

The agent fills evidence, style and slide plans using the templates as examples.
A detailed research report covers necessary background, the problem, mechanism/methods,
evidence, comparisons/synthesis and limitations, plus the user's progress and next
steps where the materials support them. An explicit single-paper talk centers on
that paper; the report default does not override the accepted presentation type.

Without another requested style or template, the agent uses the built-in synthetic
[`academic-navigator` style](../skills/research-ppt/assets/academic-navigator/):
title-information cover, separate background, a single active navigation fill without
a redundant underline, body-title rules, lower-right current-page badges and semantic
text groups. Peer cards share dimensions/padding and clear gutters across pages;
evidence-image carriers retain their own aspect ratios. New workspaces receive its
page-chrome and grouping policies; user overrides take precedence. The agent still reads
the current ppt-master template contract, adapts the talk's sections and reviews the
actual PPTX. This is a style starting point, not an automatic import command.

Keep main slides within the agreed speaking time. Put supporting derivations,
secondary comparisons and additional conditions in useful speaker notes and genuinely
hidden backup slides. There is no fixed page count; dense slide text is not a
substitute for explaining the research. An illustration can use a native teaching
example without a paper image; label it explicitly. Every slide still needs a
reading order, takeaway, source/illustration link and useful notes.

```bash
python ./skills/research-ppt/scripts/workflow.py preflight \
  --project outputs/synthetic-research-report --out outputs/synthetic-research-report/qa/preflight.json
python ./skills/research-ppt/scripts/workflow.py handoff \
  --project outputs/synthetic-research-report --run-id run-01
```

Give `outputs/synthetic-research-report/handoff/run-01/handoff.md` to the agent role executing ppt-master.
The bundle contains immutable preparation snapshots with references to local private
source/asset files; it is not automatically uploaded. Read the backend's current skill,
choose the route its current documentation requires, and map the prepared material into it.
Use commands documented for that checkout; do not manufacture an upstream
specification or confirmation.

## 5. Produce with ppt-master

Production stays in `outputs/synthetic-research-report/production/` and follows the current upstream runtime.
Do not modify the upstream submodule to hold talk outputs. The backend may refine layout
within the communication contract. A change in claims/page roster/time allocation goes
back to preparation and needs a new handoff. Obtain a real PPTX and `build_receipt.json`.

The receipt includes backend path/revision, documents read, commands actually executed,
`handoff_manifest_sha256`, `pptx_sha256`, output paths and limitations. Begin with the
pending receipt template; populate it only from observed production results. The helper
cannot certify that a backend command or document-reading claim actually occurred.

## 6. Audit and render the actual final artifact

Use the actual produced path if it differs from `exports/synthetic-research-report.pptx`
below. Keep earlier accepted versions when making revisions.

```bash
python ./skills/research-ppt/scripts/decktools.py audit \
  --pptx outputs/synthetic-research-report/exports/synthetic-research-report.pptx \
  --plan outputs/synthetic-research-report/design/slide_plan.json --out outputs/synthetic-research-report/qa/machine-v1.json
python ./skills/research-ppt/scripts/decktools.py render-pptx \
  --pptx outputs/synthetic-research-report/exports/synthetic-research-report.pptx --include-hidden \
  --out outputs/synthetic-research-report/qa/render-v1
python ./skills/research-ppt/scripts/decktools.py montage \
  --images outputs/synthetic-research-report/qa/render-v1/pages --out outputs/synthetic-research-report/qa/montage-v1.png
python ./skills/research-ppt/scripts/workflow.py review-init \
  --project outputs/synthetic-research-report --pptx outputs/synthetic-research-report/exports/synthetic-research-report.pptx \
  --handoff outputs/synthetic-research-report/handoff/run-01 \
  --render-report outputs/synthetic-research-report/qa/render-v1/render_report.json \
  --out outputs/synthetic-research-report/qa/review-v1.json
```

`render-pptx` uses LibreOffice/soffice; another actual PPTX renderer may be used if it
produces a truthful equivalent source-hash, all-slide mapping and image manifest. Exposing
hidden slides is done through a temporary ZIP/XML edit, not by rewriting native objects.
The original PPTX is never modified. Render outputs require a fresh directory.

## 7. Inspect, repair, gate

Open every slide, plus magnified figure regions where needed. Review scientific claims,
source conditions, crops, layout, notes and sources. Enter observations in the seeded
review and resolve blockers. Do not auto-fill approvals. Send localized production defects
to ppt-master; update evidence/assets/plan first when those are wrong. After changes use a
new PPTX, new render and new review, with a new handoff for preparation changes.

```bash
python ./skills/research-ppt/scripts/workflow.py gate \
  --project outputs/synthetic-research-report --pptx outputs/synthetic-research-report/exports/synthetic-research-report.pptx \
  --handoff outputs/synthetic-research-report/handoff/run-01 \
  --render-report outputs/synthetic-research-report/qa/render-v1/render_report.json \
  --audit outputs/synthetic-research-report/qa/machine-v1.json \
  --review outputs/synthetic-research-report/qa/review-v1.json \
  --receipt outputs/synthetic-research-report/production/build_receipt.json \
  --out outputs/synthetic-research-report/qa/final-gate-v1.json
```

The gate checks metadata, provenance and artifact consistency; it does not infer that a
reviewer understood the research materials or synthesis. Keep review evidence, not just a boolean pass.

## 8. Deliver and improve

Render the final PPTX again without `--include-hidden` into a fresh directory for
the visible-only PDF; `--out` names that directory, not a PDF file. For example:

```bash
python ./skills/research-ppt/scripts/decktools.py render-pptx \
  --pptx outputs/synthetic-research-report/exports/synthetic-research-report.pptx \
  --out outputs/synthetic-research-report/qa/render-visible-v1
```

This emits `qa/render-visible-v1/main_slides.pdf` within the workspace. Verify that
the visible-slide mapping and PDF match the final PPTX, then copy those verified
bytes to the agreed `output_files.pdf` path, defaulting here to
`exports/synthetic-research-report-preview.pdf`. Record the delivered PDF's hash
and provenance from the visible render. Preserve existing versions; use a new
render directory and delivery version when revising. The `-preview.pdf` is the
actual visible-slide PDF; keep the all-slide QA render, including hidden backups,
in its own directory and retain its review records.

Export speaker notes to Markdown through the actual backend or a documented
extraction, defaulting here to `exports/synthetic-research-report-notes.md`.
Use existing `output_files` paths and user overrides rather than changing them to
adopt these defaults.
Provide real paths, page/backup counts, planned time, actual backend revision, editable/raster
scope and known limitations. Without rendering, label the output an unvalidated draft.

Source packages for the private user and commits to this public skill repository are
separate decisions. Do not put private inputs, paper figures, logos, fonts or credentials
in the public repository. Improve shared rules with synthetic regression tests.
