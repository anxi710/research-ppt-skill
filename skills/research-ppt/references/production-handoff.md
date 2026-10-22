# Production delegation contract

## Ownership

Research PPT Skill owns evidence and communication decisions, prepared assets, acceptance
criteria and independent review. ppt-master owns its internal routing, specifications,
layout implementation, native object generation and export. Use its full current
capabilities through its documented route; keep production implementation in the backend.

ppt-master may also contain planning/verification capabilities. Our preparation is an
input brief, not a substitute for its mandatory runtime gates. Reconcile overlapping
planning by mapping our audience/claims/assets into its current schema; never impersonate
user confirmation or manufacture a backend lock. Report genuine conflicts to the user.

## Discover current backend

The repository helper `scripts/upstream.py update` updates the configured branch for a
new job. It is maintenance, not a production command. A standalone installation may
instead be supplied as an explicit local path; resolve it against the request's working
directory if relative, then record its real absolute location. Do not infer a usable
local directory from a public URL or from a previous session.

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
4. a pending receipt template for the backend to fill after actual production;
5. for the default Academic Navigator contract, its template workspace snapshot,
   exact root and per-file fingerprints.

The agent must provide this handoff to the backend. The files are not automatically sent
to an API; the helper performs no model calls. Source/asset paths remain local, and work
happens under `production/`, not inside the upstream submodule.

Preserve the brief's presentation type and depth, the accepted report-wide narrative and
the slide plan's coverage record. A detailed research report must not become an abstract
deck or a string of disconnected paper summaries during layout. Keep explanatory notes,
source distinctions, key comparisons and planned hidden backups; propose scope/time
changes rather than deleting necessary explanation to fit a template.

Pass the accepted style profile and each page's visual requirements from `story-and-style.md` to the backend.
Include the actual section mappings and exceptions. Preserve each asset's role and provenance.
Use display-ready figure/table crops on slides. Keep full captions and source-page context in evidence and notes.
Keep decoding legends and consequential conditions visible.
Do not use external context or generated illustrations as evidence for the focal results.
Record how the backend implements the accepted font configuration.
Inspect the exported font faces, text frames and line breaks.

## Apply the selected template

For new `design_contract_version: 1` briefs, preserve init's `design_mode` and its matching
style contract; resolve older pending template decisions before preflight. The default
`design_mode: "academic_navigator"` and `design_contract.mode: "academic_navigator"` select the
workspace at `<absolute skill directory>/assets/academic-navigator/`. A real user choice
may select a replacement with both modes set to `user_override`; retain its instruction and reason.
An explicit no-template choice under that mode requires the real supporting brief/intake
instruction; it does not require a template snapshot or application receipt. The default
cannot take this exception merely because its selection or installation is unfinished.
Do not leave `pending_default`, call an unapplied template applied, or substitute a basis
such as free layout without imported prototypes for the required default.

The parent helper's snapshot and receipt contract below is required only for
`academic_navigator`. Apply an explicitly selected replacement through the current
backend's own template workflow and retain its genuine selection/application evidence;
`user_override` does not require the same parent snapshot or record schema.

Snapshot the selected package into the immutable handoff, retaining `templates/` and
any portable sibling asset folders. Record the exact workspace root and fingerprints
of the spec, prototypes and assets. Pass that snapshot root as the explicit template
input to the backend, not a bare name, a relative style label, or only its inner
`templates/` directory. A later change to the skill's installed assets must not change
what an existing handoff means.

The handoff manifest's `template` entry records `source_root`, `snapshot_root`, `manifest`
and `sha256`. `snapshot_root: "template/"` is relative to that handoff; resolve it to an
absolute path for the backend. `template/manifest.json` records the original
`source_root` and a `files` map of snapshot-relative paths to hashes. Its digest is the
template identity carried into the production receipt.

Read the current backend's template contract and selected production route. For a backend
that separates candidate selection from application, submit this exact root as an
explicit candidate at its template-choice stage. Preserve its real user-confirmation
requirements; when the actual user has delegated that choice, follow its documented
delegation path without fabricating confirmation state. Read only candidate frontmatter
before selection where required. After selection, validate and install the workspace
through the backend's supported mechanism, then read its complete project-local specs
and SVG prototypes for planning. Do not let an omitted root silently initialize free
design: ordinary backend requests may default to that route, so the parent default must
be an explicit template input. A backend choice to use no template requires a real user
override recorded in the brief and style contract. A rejected or incompatible template
requires a stated resolution; it is not permission to silently discard the design contract.

Save the backend's explanation of template application.
Record the installed package and the mapping from page roles to prototypes.
Explain the adaptations and how they preserve the accepted style rules.
A style-only or flat reuse label does not waive those rules.
Do not force the talk's chapters, scientific content or page count to match the prototypes.

For the default contract, complete the receipt's `template_application` after actual
installation: `status: "applied"`, `handoff_template_sha256`, an absolute
`installed_template_root`, and `application_record: {path, sha256}`. The record path is
relative to the private workspace. Start from the handoff's
`template_application.example.json`; do not mark its pending example as a real receipt.

The application record repeats `handoff_template_sha256` and `installed_template_root`,
records the concrete explanation in `application_notes`, and maps every source entry
in `files` to `{path, sha256}` for the actual installed file. Keys are snapshot-relative
source paths; each mapped `path` is relative to the installed root and must identify a
distinct real file. A backend may qualify a spec filename and add its documented
installation-provenance line. Record actual installed hashes: SVGs retain their source
bytes; specs must match the source or only have the supported provenance insertion.
Do not generalize that exception to arbitrary template edits. Check the complete mapping
against the immutable snapshot and real files; a pending receipt, claimed inspiration
or copied template folder alone does not prove application. This is provenance and
acceptance evidence owned by the parent skill, not a replacement backend schema, design
lock or production engine.

## Preserve communication and output requirements

Pass the communication contract and reference observations from the style profile to the backend.
`display_title` and `on_slide_text` contain the intended visible copy.
The planning fields are `question`, `topic`, `takeaway`, reading order and notes.
Unless the plan selects them for display copy, use them only for planning and speaking.
Apply the recorded terminology, citation placement, opening/closing and backup choices.
Keep full source locators in notes. Keep necessary experimental conditions on the slide.
Use the backend's supported math route. Inspect subscripts, superscripts and time indices after export.

Pass `brief.json`'s `project_name` and `output_files` to the backend.
The default workspace is `./outputs/<project-name>/` relative to the request's working directory.
Default delivery paths are `exports/<project-name>.pptx`, `exports/<project-name>-preview.pdf` and `exports/<project-name>-notes.md`, for requested formats only.
Honor explicit user names and paths. Keep `output_files` entries distinct, relative to the workspace and inside it.
The backend can use its own build filenames.
Before final hashing, rendering and review, put delivery candidates at the declared paths.
Preserve previous versions. Record the actual paths in the receipt.
If you rename or replace a reviewed file, inspect the delivered bytes again. Then update its artifact record.
The preview PDF contains visible slides rendered from the final PPTX.
Keep separate renders of all slides, including hidden backups, for QA.
For resumed workspaces, preserve saved filenames.

## Requested output

A real PPTX with native editable text/annotations when requested, original source figures,
notes on each page, and genuine hidden flags for backups. Return build inputs/source paths,
commands actually run, backend identity, exported paths, source hashes and known limits.
Do not convert entire slides into background screenshots and call the result editable.

If the current backend has no documented control for hiding slides, preserve its raw
export and report, then make a separate delivery copy with a limited ZIP/XML visibility
repair. Resolve the planned slide order through `ppt/presentation.xml` and its
relationships; do not assume a part filename equals its physical page number. Set
the unqualified `show="0"` attribute on each planned backup's `<p:sld>` root, retaining
visible pages' intended state. If `docProps/app.xml` already has `HiddenSlides`, update
its count. Preserve every other package part and slide-content node; do not regenerate
the deck, alter its content, or resave it through a presentation library just to set
visibility. Read back the final order and flags against the plan. Record the repair
and both artifact paths; hash, render and independently audit the exact delivery copy.
The backend's raw-export report does not validate this changed copy. An unresolved
plan/part mapping or hidden-state mismatch blocks acceptance.

Inspect representative pages before expanding the deck, within the backend's allowed
workflow. Line breaks, grouping, font fit and mathematically equivalent typesetting can
change presentation without rewriting the approved copy. A wording/page-count/claim/figure
change is a contract change, not a silent design tweak.
Send it back to the orchestrator, update the plan, then take a fresh handoff snapshot.

## Revision requests

Each issue contains `id`, `slide_id`, `category`, `severity`, evidence/screenshot, requested
change and acceptance criteria. Cosmetic fixes preserve evidence, numeric labels, figure
identity and unaffected slides. Evidence corrections update the preparation snapshot first.
The backend's repair receipt states which slides changed, what remains unresolved, and
where the new artifact exists. The orchestrator rerenders and rechecks it independently.

When adding a background to an existing native content unit, keep it beneath that
unit's text and evidence in the same semantic group through the backend's supported
edit route. Inspect the final PPTX for occlusion and stacking order; SVG order alone
does not establish the exported native order.
Give each editable paragraph its planned line width through the backend's current
text-frame contract. Widening a surrounding panel does not widen its child text boxes;
check the actual PPTX for unintended wrapping before accepting consistent-looking cards.
