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
4. a pending receipt template for the backend to fill after actual production.

The agent must provide this handoff to the backend. The files are not automatically sent
to an API; the helper performs no model calls. Source/asset paths remain local, and work
happens under `production/`, not inside the upstream submodule.

Preserve the brief's presentation type and depth, the accepted report-wide narrative and
the slide plan's coverage record. A detailed research report must not become an abstract
deck or a string of disconnected paper summaries during layout. Keep explanatory notes,
source distinctions, key comparisons and planned hidden backups; propose scope/time
changes rather than deleting necessary explanation to fit a template.

Pass display-ready figure/table crops separately from full captions and original-page
evidence. The backend uses the display crop, not an uncropped source page. Keep decoding
legends and consequential conditions visible; use notes for the removed prose caption.
Carry the named typography roles, limited palette and any section-navigation settings
with the per-page `section_id` mapping. Carry the accepted cover-only fields and separate
background page, coordinated page chrome (navigation, title rule and page badge), and
the semantic grouping/reading order of multi-passage pages. Specify one active nav
fill without a redundant underline, peer component dimensions/padding, and minimum
gutters; keep the body-title divider. Separate image carriers from commentary classes.
Pass external context images with original-source/version attribution and their
context-only role, not as evidence of the focal paper's results. Mark generated concept
assets separately, carry their prompt/tool/model/output provenance, and use native text
for labels; do not assign paper citations to generated pixels. Give exact template asset
paths for the default `assets/academic-navigator/` style, or for the user's selected
replacement. New workspaces carry the default page-chrome and grouping policies;
complete actual section labels and mappings during planning rather than importing
a fixed chapter list. Read
the current backend's template contract and supported route; a bundled SVG or style
profile does not imply automatic structural import. These are presentation requirements to implement
through the backend's current instructions, not a replacement backend schema or engine.

Carry the style profile's communication contract and concrete reference observations into
the backend brief. `display_title` and `on_slide_text` are the intended visible copy;
`question`, `topic`, `takeaway`, reading order and notes are planning/speaking fields unless
explicitly included in display copy. Apply the recorded terminology, citation placement,
opening/closing and backup choices. Do not restore a long bibliographic footer because an
optional generic profile uses one; retain full source locators in notes and necessary
experimental conditions on the slide. Use the backend's supported math route and verify
subscripts, superscripts and time indices after export.

Carry `brief.json`'s `project_name` and `output_files` into production. The default
workspace is `./outputs/<project-name>/` relative to the request's working directory,
with delivery files `exports/<project-name>.pptx`, `exports/<project-name>-preview.pdf` and
`exports/<project-name>-notes.md` for requested formats. Explicit user names/paths
win. Backend build filenames may follow its current route; stage delivery candidates
at the declared paths before final hashing, rendering and review. Preserve previous
versions and record the actual paths in the receipt; never rename or replace a file
after review without verifying the delivered bytes and updating the artifact record.
The preview PDF contains visible slides rendered from the final PPTX. Keep separate
all-slide QA renders with hidden backups; preserve saved names on resumed workspaces.

## Requested output

A real PPTX with native editable text/annotations when requested, original source figures,
notes on each page, and genuine hidden flags for backups. Return build inputs/source paths,
commands actually run, backend identity, exported paths, source hashes and known limits.
Do not convert entire slides into background screenshots and call the result editable.

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
