# Runbook

The commands below are deterministic helpers for an agent. They do not read the paper
semantically, choose a narrative, judge visual correctness, or produce the talk autonomously.
Use Python 3.10+ and a current tool-capable host. Run from this repository's root or use
absolute script paths when the skill is installed separately.

## 1. Setup and new workspace

```bash
python -m pip install -r requirements.txt
python scripts/upstream.py update --out ../backend-observation.local.json
python skills/research-ppt/scripts/workflow.py init \
  --project ../paper-talk \
  --source /path/paper.pdf \
  --template /path/optional-reference.pptx \
  --minutes 27 --language zh-CN \
  --audience "AI researchers outside this paper subfield"
```

Omit `--template` without a reference. Repeat `--source` for multiple source files.
Inputs are copied into the private workspace and fingerprinted. Update the exact source
version, requested sections, Q&A policy and explicit assumptions in `brief.json`.
An initialized workspace deliberately fails preflight until evidence/style/plan are ready.

`upstream.py update` requires Git/network access and a real gitlink. It follows the current
configured branch, does not discard dirty changes and does not execute upstream code.
Record its output, then read the current backend entry instructions before production.

## 2. Read sources and inspect style

```bash
python skills/research-ppt/scripts/decktools.py extract-pdf \
  --pdf ../paper-talk/inputs/source_01.pdf --out ../paper-talk/analysis/paper.md
python skills/research-ppt/scripts/decktools.py render-pdf \
  --pdf ../paper-talk/inputs/source_01.pdf --pages 1-5 \
  --out ../paper-talk/qa/source-pages --dpi 160
python skills/research-ppt/scripts/decktools.py inspect-template \
  --pptx ../paper-talk/inputs/template.pptx --out ../paper-talk/analysis/template
```

Read exact definitions, main results and necessary supplements. Open page images for
figures/tables. Render the reference PPTX when present; statistics alone miss theme
inheritance and image content. The helper avoids OCR and uses PDFium for PDF rendering.
Keep any separately generated background outside the paper-derived evidence ledger or
label it as external background with its own source.

## 3. Prepare original figures

Populate `analysis/figure_manifest.json` from actual inspected PDF regions. Coordinates
are top-left-origin PDF points on an unrotated page; do not paste screenshot pixels.
The crop helper accepts one PDF at a time; for multiple sources, pass a source-filtered
crop manifest and merge the verified records into the workspace's figure inventory.

```bash
python skills/research-ppt/scripts/decktools.py crop \
  --pdf ../paper-talk/inputs/source_01.pdf \
  --manifest ../paper-talk/analysis/figure_manifest.json \
  --out ../paper-talk/assets/paper --dpi 360
python skills/research-ppt/scripts/decktools.py montage \
  --images ../paper-talk/assets/paper --out ../paper-talk/qa/figure-montage.png
```

The crop report records dimensions, hashes and **pending** review. Inspect each figure,
then enter its `path`, `sha256`, `review_status: verified` and review observations in the
figure manifest. Do not change pending status before actually checking axes/legends.
Unusual page boxes, rotation and user units may require a separately normalized PDF and
new provenance. Verify a known geometry region before bulk cropping such documents.

## 4. Plan, preflight and handoff

The agent fills evidence, style and slide plans using the templates as examples.
An illustration can use a native teaching example without a paper image; label it explicitly.
Every slide still needs a reading order, takeaway, source/illustration link and useful notes.

```bash
python skills/research-ppt/scripts/workflow.py preflight \
  --project ../paper-talk --out ../paper-talk/qa/preflight.json
python skills/research-ppt/scripts/workflow.py handoff \
  --project ../paper-talk --run-id run-01
```

Give `../paper-talk/handoff/run-01/handoff.md` to the agent role executing ppt-master.
The bundle contains immutable preparation snapshots with references to local private
source/asset files; it is not automatically uploaded. Read the backend's current skill,
choose the route its current documentation requires, and map the prepared material into it.
Do not reuse historic CLI flags or manufacture an upstream spec/confirmation.

## 5. Produce with ppt-master

Production stays in `../paper-talk/production/` and follows the current upstream runtime.
Do not modify the upstream submodule to hold talk outputs. The backend may refine layout
within the communication contract. A change in claims/page roster/time allocation goes
back to preparation and needs a new handoff. Obtain a real PPTX and `build_receipt.json`.

The receipt includes backend path/revision, documents read, commands actually executed,
`handoff_manifest_sha256`, `pptx_sha256`, output paths and limitations. Begin with the
pending receipt template; populate it only from observed production results. The helper
cannot certify that a backend command or document-reading claim actually occurred.

## 6. Audit and render the actual final artifact

Use the produced path in place of `exports/talk.pptx` below.

```bash
python skills/research-ppt/scripts/decktools.py audit \
  --pptx ../paper-talk/exports/talk.pptx \
  --plan ../paper-talk/design/slide_plan.json --out ../paper-talk/qa/machine-v1.json
python skills/research-ppt/scripts/decktools.py render-pptx \
  --pptx ../paper-talk/exports/talk.pptx --include-hidden \
  --out ../paper-talk/qa/render-v1
python skills/research-ppt/scripts/decktools.py montage \
  --images ../paper-talk/qa/render-v1/pages --out ../paper-talk/qa/montage-v1.png
python skills/research-ppt/scripts/workflow.py review-init \
  --project ../paper-talk --pptx ../paper-talk/exports/talk.pptx \
  --handoff ../paper-talk/handoff/run-01 \
  --render-report ../paper-talk/qa/render-v1/render_report.json \
  --out ../paper-talk/qa/review-v1.json
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
python skills/research-ppt/scripts/workflow.py gate \
  --project ../paper-talk --pptx ../paper-talk/exports/talk.pptx \
  --handoff ../paper-talk/handoff/run-01 \
  --render-report ../paper-talk/qa/render-v1/render_report.json \
  --audit ../paper-talk/qa/machine-v1.json \
  --review ../paper-talk/qa/review-v1.json \
  --receipt ../paper-talk/production/build_receipt.json \
  --out ../paper-talk/qa/final-gate-v1.json
```

The gate checks metadata, provenance and artifact consistency; it does not infer that a
reviewer genuinely understood the paper. Keep review evidence, not just a boolean pass.

## 8. Deliver and improve

Render once without `--include-hidden` into a new directory for the visible-only PDF.
Export speaker notes to Markdown through the actual backend or a documented extraction.
Provide real paths, page/backup counts, planned time, actual backend revision, editable/raster
scope and known limitations. Without rendering, label the output an unvalidated draft.

Source packages for the private user and commits to this public skill repository are
separate decisions. Do not put private inputs, paper figures, logos, fonts or credentials
in the public repository. Improve shared rules with synthetic regression tests.
