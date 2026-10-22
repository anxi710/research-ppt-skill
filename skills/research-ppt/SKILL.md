---
name: research-ppt
description: >
  Prepare research presentations from supplied papers, notes, reports and results.
  Review and revise their final files. Use for research reports, paper talks,
  journal clubs, literature reviews, progress reports and scientific tutorials.
  Own evidence, audience, narrative, style, figures, handoff and independent review.
  delegate slide authoring and export to the current ppt-master backend.
license: MIT
metadata:
  version: "0.4.2"
---

# Research PPT

This skill requires file access, image inspection and code execution.
Production also requires ppt-master and a real PPTX renderer.
This skill owns preparation and independent review.
ppt-master is the backend that produces the slides.
Follow its current instructions and required approval steps.
Do not build another slide production engine.
Keep accepted research claims unchanged.

Follow user requirements before defaults.
If the user does not specify the talk type, propose `research_report` with `detail_level: detailed`.
Organize the report around the research question.
A single source is enough.
Keep the requested scope for paper talks, reviews, progress reports and tutorials.
Detail means enough explanation, evidence and notes within the time budget.
It does not require a fixed slide count or dense text.
Repository maintenance does not start presentation intake.

## Read by stage

Before starting a stage, read its reference.
Runtime instructions and scripts are inside this skill.
Repository maintenance is separate and optional.

| Work | Reference |
|---|---|
| Intake, source reading and evidence | [preparation.md](references/preparation.md) |
| Audience, narrative, style and figures | [story-and-style.md](references/story-and-style.md) |
| Backend discovery, template application and handoff | [production-handoff.md](references/production-handoff.md) |
| Final render, inspection, repair and delivery | [review-and-revision.md](references/review-and-revision.md) |
| User supplies an edited final deck | [reference-calibration.md](references/reference-calibration.md) |
| Optional concept images or image-service setup | [image-generation.md](references/image-generation.md) |
| Requested environment setup | [environment-setup.md](references/environment-setup.md) |

## Workspace and scripts

Before changing directories, resolve the request's working directory, supplied paths and this skill's real directory.
Run bundled scripts by their resolved paths.
Keep each talk in a private workspace.
To resume a talk, use its saved files instead of initializing again.
Do not overwrite accepted inputs, handoffs, reviews or earlier deliverables.

For every new talk, run `scripts/workflow.py init`.
Supply a short name based on the topic through `--name`.
Supply the selected `--source` files, `--minutes`, `--language` and `--audience`.
Ask for missing required values first.
Do not invent values to satisfy the command arguments.
The default workspace is `./outputs/<project-name>/` under the request's working directory.
Use `--project` to set another location.
Init handles safe names and duplicate names and prints the actual path.

A design contract records the accepted visual rules.
A handoff is a fixed copy of the preparation files.

| Files | Purpose |
|---|---|
| `brief.json` | Requirements, sources, output paths and real intake confirmation |
| `analysis/evidence.json`, `analysis/figure_manifest.json` | Claims, locators and verified assets |
| `analysis/backend.json` | Actual backend path/revision and document observations |
| `design/style_profile.json`, `design/slide_plan.json` | Design contract, coverage, page jobs and notes |
| `handoff/run-*/` | Fixed preparation and default-template copies |
| `production/` | Backend-owned workspace |
| `qa/`, `exports/` | Audits, actual renders, reviews and accepted deliverables |

Preserve init's generated fields when filling requirements.
JSON examples document the format.
Do not replace real paths or contracts with a reduced example.
Existing accepted workspaces retain their saved conventions and filenames.

Use `python <skill-dir>/scripts/workflow.py --help` for arguments:

| Command | Required use |
|---|---|
| `init` | Create each new workspace and defaults |
| `intake` | Generate the requirement snapshot before recording actual acceptance |
| `preflight` | Test preparation records before production |
| `handoff` | Repeat preparation tests and create a fixed copy for the backend |
| `review-init` | Link a pending review form to the final PPTX's rendered images |
| `gate` | Test final records, file hashes and review coverage before delivery |

Run these commands instead of simulating their results in prose.
Use `decktools.py --help` for optional extraction, crop, montage, PPTX audit and rendering helpers.
The scripts test records, file contents and hashes, which identify file bytes for change detection.
They cannot establish user consent or judge science and readability.

## 1. Agree on the brief

Follow `references/preparation.md`.
List the supplied materials before detailed evidence reading.
Reuse known requirements.
Ask only about missing or conflicting requirements: audience, purpose, duration/Q&A, language, scope/depth, style and outputs.
Distinguish supplied requirements, proposed defaults and choices that the user delegates.

Record the actual acceptance or an existing instruction that authorizes the choices and further work.
Save that response with the requirement snapshot from `intake`.
A generic request to make a PPT does not delegate decisions.
When resuming, reuse accepted requirements.
Obtain acceptance only for material changes without prior authorization.
This acceptance does not replace the backend's required approvals.

## 2. Prepare evidence and design

Follow `references/preparation.md` and `references/story-and-style.md`.
Read exact source versions.
Inspect original figures and tables.
Separate published findings, user results, author interpretations, presenter analysis and teaching examples.
Record the source location and scope for each key claim.
State contradictions and evidence gaps.
Notes about a paper do not replace the original.
Follow offline and source-only limits.
If evidence is missing, obtain authorization before expanding scientific claims or the literature scope.

Build one coherent argument for this audience. Each page needs a job, core visual,
evidence links, final `display_title`/`on_slide_text`, reading order, notes, duration
and visible/backup status. Planning fields are not extra display copy.
Record which topics the talk covers or excludes.
Keep needed reasoning in the main talk.
Put supporting detail in notes or hidden backup slides.
Fit main slides to the speaking budget after Q&A.

For the default design, apply `assets/academic-navigator/`.
Without `--template`, init sets `brief.design_mode: academic_navigator` and the matching versioned style contract.
It also records the real template root/spec, `status: selected` and `applied: false`.
Keep these fields.
Selection does not approve the brief or prove that the backend applied the template.

The default separates the cover from the background explanation.
Main-talk section tabs fit their labels and align with the title's left edge, with visible gaps and one active fill.
Body pages have title dividers and bottom-right badges with the current page number.
Font roles use Times New Roman and Microsoft YaHei.
The default uses one native accent color and consistent groups of related content.
Plan section labels, page mappings and exceptions from the actual talk.
Read `references/story-and-style.md` and the generated profile for detailed rules.

If the user explicitly requests another style/template, set both brief and style modes to `user_override`.
Record the actual instruction and reason.
“Clean academic” or delegated design does not waive the default.
Preserve accepted contracts from earlier workspaces.

Use original figure/table bodies.
Keep prose captions in notes and local evidence.
Retain axes, legends, units, uncertainty and interpretive context. Do not redraw or
generate empirical plots. Native explanations and optional generated concept images
must be distinguishable from evidence and retain source records. Match supplied references
without copying old identities, claims or logos.

Before production, make sure that `preflight` passes.
Inspect the sources and assets.
Make sure that the plan is teachable and fits the time budget.
Valid metadata alone does not establish scientific or visual quality.

## 3. Delegate production

Follow `references/production-handoff.md`.
Resolve the real ppt-master checkout.
Read its current entry instructions before invoking it.
For a new job, update its configured branch when network access and user scope permit.
Record the actual revision and any update failure.
Keep that revision stable for the run.
Do not describe an unfetched checkout as latest.

Run `handoff` to create the fixed preparation copy.
Pass its files and constraints through the backend's documented route.
For the default, pass the copied template workspace's absolute root as an explicit template input.
A style name alone can fall back to free design.
Follow the backend's selection/install steps and required approvals.
Read template prototypes only at the permitted stage.
Keep source claims, scope, figure identity and accepted copy intact.

Within the backend's allowed workflow, inspect representative explanation and dense-evidence pages before expanding the deck.
Obtain a real PPTX and an accurate build receipt with paths, revision, commands and limitations.
For default mode, also obtain the installed template's file records and its hashed `template_application` record.
Installation is not visual approval.

## 4. Review, repair and deliver

Follow `references/review-and-revision.md`.
Audit the final PPTX against the plan.
Render it with a real PPTX renderer, including hidden backups.
Run `review-init` to create the pending review form.
Inspect every full slide and necessary crop.
Record concrete observations.
SVG previews, montages and backend tests do not replace inspection of the final PPTX.

Make sure that claims agree with sources.
Inspect figure context, notes, fonts, navigation, page dividers, page badges, content groups and legibility at presentation size.
For default mode, complete the template-application and projection-readability reviews.
Never mark unseen pages passed.

If evidence or the plan is wrong, repair the preparation files.
Then create a new handoff.
Send layout or export defects to ppt-master.
Enlarge, split or rearrange unreadable evidence rather than shrinking all fonts.
Render changed files again.
Inspect the complete final deck.
After structural changes, reconcile page order, topic coverage, backups, notes and time.
Continue routine repairs within the accepted scope.
Do not infer success from the number of retries.

Run `gate` against the final files.
Resolve all errors that block delivery.
A changed file or contract invalidates earlier approval.
Do not rewrite hashes or copy pass values to pretend a new review occurred.
If no renderer is available, label the output an unvalidated draft.

Deliver requested, existing files at the brief's `output_files`, normally
`exports/<project-name>.pptx`, `exports/<project-name>-preview.pdf` and
`exports/<project-name>-notes.md`. The preview contains visible slides only.
Keep backups in the images for the full review.
Explain which content is editable, which content is an image, and what limitations remain.
Keep private papers, decks, identities, results, credentials and fonts out of public skill releases.
Use synthetic fixtures to test skill improvements.
