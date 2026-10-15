# Review, revision and delivery

## Three independent questions

1. **Content:** Does the slide accurately represent the source and the evidence strength?
2. **Presentation:** Can this audience read and understand it in the available time?
3. **Artifact:** Does the exported file actually contain and render what was intended?

The production tool's successful exit code answers none of these completely.

## Structural and rendering checks

Verify ZIP/XML relationships, slide count/order, native text existence, note content, hidden
flags and time-budget consistency. Box-boundary warnings need human/agent interpretation:
intentional bleed is possible. Grouped/rotated shapes, theme inheritance and SVG handling
require visual review even if no machine warning appears.

Render the final PPTX in a real renderer. Use a temporary ZIP/XML-only copy to expose hidden
slides for QA; do not resave the deck through a library merely to toggle visibility, because
unsupported advanced objects could be altered. Keep the original file unchanged. Record
renderer identity, slide mapping, source PPTX hash and per-image hashes. The visible-only PDF
is a separate delivery; all-slides QA must include every backup.

Inspect all full-size slides and necessary detail crops, not just the montage. Confirm
figure axes/legends/panels, image aspect ratio, readable fonts, title/figure agreement,
citation placement, annotation placement, whitespace and excessive density. Read the notes.
Check that critical definitions precede results and that teaching examples are labelled.

On the actual PPTX renders, check display crops against their full source context: the
paper's prose caption and adjacent text are removed unless explicitly requested, while
data legends, table headers, units and consequential conditions remain readable. Check
that explanations removed from the slide are present in notes or local evidence. Inspect
each native text role for the agreed family, size and weight across pages, and compare
emphasis colors with the limited palette. Theme/font statistics support this review;
they do not replace seeing the final rendered text. Source-figure lettering and recorded
cover/backup exceptions are reviewed separately.

When section navigation is enabled, check every applicable page for the same ordered,
consistently spaced top labels, the correct single active section, agreement with its `section_id`,
and clearance from the title and figures. The active fill should not gain a redundant
underline; do retain the separate body-title divider. A correct SVG strip can still shift or lose
fonts in PPTX export. Record these findings in the page's layout/reference review along
with any explicit exceptions.
When the corresponding policies are enabled, the helper also seeds pending
`figure_framing`, `section_navigation`, `typography_consistency` and `palette_consistency`
checks. Complete them from actual inspection, not from the presence of valid settings.

Review page chrome as a complete system: navigation aligns across content pages, the
title divider clears the title/figure, and the current-page-only badge stays at the
agreed lower-right position with its background and numbering convention. Check
declared cover/backup exceptions rather than adding body chrome indiscriminately.
For a title-only cover, verify that it contains only approved title/metadata and that
background explanation appears on its own planned page. On multi-passage pages, inspect
whether headings, numbers or containers expose the intended semantic groups and reading
order without crowding, decorative repetition or separating a qualifier from its claim.
Compare peer component heights, padding and edge treatment both within and across
pages; differing evidence-image carriers need not match commentary boxes. Confirm that
minimum gutters remain visibly clear and no border, shadow or text crowds its neighbor.
Any pending chrome/grouping checks require judgment from actual PPTX renders; schema
validation and template previews cannot pass them.
The helper seeds pending `page_chrome` when that policy is present and
`content_grouping` when its policy is enabled. Complete them with concrete observations
about the rendered cover, recurring elements and passage hierarchy.
For new workspaces, check the built-in research style unless the user chose an
override: title-information-only cover with separate background, continuous physical
page numbers, body title separators, meaningful passage groups and coherent active
navigation. A valid default policy is still pending evidence of correct rendering.

For communication-contract workspaces, `audience_copy` and `reference_match` are separate
pending checks on every page. Compare final titles/body with the display plan, read the
titles as one outline and check terminology and direct wording. Compare page composition,
font roles, figure size, annotations and citation placement with the recorded reference
pages or style basis. Character counts cannot approve density. Inspect equations and
time indices, and title fit after a font/editor change. Review comments must describe
concrete observations, not merely repeat the check names. Legacy reviews remain valid
under their original contract; do not copy approvals into a changed contract.

## Scientific review

Compare the final deck and notes with the agreed presentation type, depth and coverage
record. For an integrated report, verify that material from different sources answers
the central questions coherently, and that published evidence, user results and analysis
remain distinct. Check explanations of prerequisites, mechanisms, setup and limitations
where needed. Check contextual images against their original source and version,
verify attribution, and ensure they are not presented as the focal paper's experiment
or as support for a new result claim. A text-only background/benchmark page needs a
deliberate reason when a useful primary-source illustration is available. Inspect
generated concept images for false scientific details, invented interfaces/data/text,
style drift and misleading evidence attribution. Missing required topics or a merely
abstract-level deck are scope defects,
even if every existing slide is visually correct. Retain exclusions and evidence gaps.

Recheck each load-bearing numeric result, denominator, threshold, evaluation unit, budget,
model condition, comparison and uncertainty. Author explanations and presenter inferences
must not become unqualified slide facts. Different experimental protocols cannot be combined
as one comparison merely because the graphics align nicely.

## Defects and repair

Use categories `evidence`, `narrative`, `asset`, `layout`, `export`, `notes` and `timing`.
A blocker prevents acceptance; a warning may remain only with a written rationale. Do not
mark unseen pages passed. A judge model is an assistant to review, not ground truth.

Send layout/export fixes to ppt-master. Send source/claim problems to preparation, regenerate
the handoff and then request backend changes. Keep previous accepted versions. After each
repair, rerender affected content and check deck-wide consistency. Review the final full deck
before acceptance. No arbitrary retry count converts a failure to a pass.

## Gate and audit trail

`review-init` creates a pending checklist—never passed entries. It binds a real all-slide
render report and a preparation handoff. Reviewer comments describe what was inspected.
`gate` checks source/asset/preparation fingerprints, final PPTX, machine report, actual render
mapping, page images and review coverage. It is a consistency gate, not a proof of scientific
or visual correctness. Hashes do not authenticate reviewer judgment.

Changing the contract, source, figure, file or render invalidates its old approval. Do not
edit old hashes or merely copy old pass values. Renderer unavailable: label output as an
unvalidated draft and describe what still needs inspection, never fabricate QA.

## Delivery and iteration

Deliver only existing artifacts. Normally: final PPTX, visible-only PDF, notes Markdown and
an authorized source package with provenance, actual backend revision and build receipt.
Use the brief's `output_files`: normally `exports/<project-name>.pptx`,
`exports/<project-name>-preview.pdf` and `exports/<project-name>-notes.md` inside the private
`./outputs/<project-name>/` workspace, relative to the request's working directory.
The preview contains the final PPTX's visible slides; do not substitute the all-slide
QA PDF that includes hidden backups. Preserve existing workspaces' saved paths and
honor user overrides. New revisions use new filenames; inspect and hash the exact
delivery copies and keep previous versions.
Record editable/raster elements and font requirements; never redistribute font binaries.

A skill release must not include the private talk's PDFs, original images, institution logos,
unpublished data, personal identities or secrets. Generalize lessons into rules and synthetic
fixtures. Permission to create a public skill repository does not imply permission to publish
all inputs used by that skill.

When the user supplies a manually edited final version, follow
`references/reference-calibration.md` to align the pair and turn repeated edits into
project-local rules. Preserve the main-deck choices without imitating accidental lost
notes, clipping or changes in evidence strength. Public improvements use synthetic data.
