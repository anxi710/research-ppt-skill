# Review, revision and delivery

## Three independent questions

1. **Content:** Does the slide accurately represent the source and the evidence strength?
2. **Presentation:** Can this audience read and understand it in the available time?
3. **Artifact:** Does the exported file actually contain and render what was intended?

The production tool's successful exit code answers none of these completely.

## Template application

For a new default design-contract workspace, begin with the immutable handoff's
template snapshot, its exact root and file fingerprints.
Compare the handoff template manifest's digest with the build receipt's
`template_application.handoff_template_sha256`. Verify `status: "applied"`, the real
`installed_template_root`, and the referenced `application_record` file/hash. The record's
matching digest/root, `application_notes` and complete `files` mapping identify the
actual spec/prototype paths and hashes. Check source-to-installed mappings, allowing
only the current backend's documented filename/provenance transformations. Read the
actual installed specs/prototypes when
needed to check a claimed mapping or adaptation. A selected template, successful copy,
matching hashes, or a sentence saying the design follows the template does not establish
that its visual elements reached the deck.

For the default, the helper seeds `template_application` as pending. Complete it from actual PPTX renders
and the accepted design contract, alongside the page-specific chrome, navigation,
typography, palette and grouping checks. Check a representative cover, explanation and
dense evidence page first within the backend's allowed production/review order, then
inspect every final page and applicable exception. Representative pages cannot approve
the unseen remainder.

For `mode: "academic_navigator"`, verify the information-only cover, separately planned
background, single-highlight navigation without an extra active underline, body-title
divider, lower-right badge showing the current physical page only, fixed native text
roles, limited accent palette, consistent peer groups/gutters and body-only source
figure crops. Compare geometry and recurring elements with the selected prototypes and
documented adaptations. An internal style-only or flat reuse label does not waive these
binding visual requirements. For `mode: "user_override"`, check the actual user instruction
and reason, then inspect the replacement's accepted rules, its actual backend selection/
application evidence and all retained requirements. This mode does not require the
default's parent snapshot or application-record schema.
An explicitly accepted no-template override does not need template installation evidence;
inspect its accepted design requirements directly. Do not invent an override after
seeing an export that lost the default design.

Missing installation/application evidence or a deck that discarded the selected design
is a production defect. Return it to the backend with concrete slide observations and
the missing required element; repair, rerender and review before acceptance. Do not pass
`template_application` merely because the other checklist fields contain pass values.

## Structural and rendering checks

Verify ZIP/XML relationships, slide count/order, native text existence, note content, hidden
flags and time-budget consistency. Box-boundary warnings need human/agent interpretation:
intentional bleed is possible. Grouped/rotated shapes, theme inheritance and SVG handling
require visual review even if no machine warning appears.

When a backend lacks hidden-slide controls, use only the limited delivery-copy
visibility repair in `production-handoff.md` before final hashing and review. Verify
that package changes are confined to the planned slide-root visibility attributes
and any existing `HiddenSlides` count; content and all other parts remain unchanged.
Read back the actual visible/hidden sequence through Presentation relationships.
Keep the raw export/report as provenance, and bind all acceptance records to the
repaired delivery copy rather than treating the raw-export report as its approval.

Render the final PPTX in a real renderer. Use a temporary ZIP/XML-only copy to expose hidden
slides for QA; do not resave the deck through a library merely to toggle visibility, because
unsupported advanced objects could be altered. Keep the original file unchanged. Record
renderer identity, slide mapping, source PPTX hash and per-image hashes. The visible-only PDF
is a separate delivery; all-slides QA must include every backup.

Inspect all full-size slides and necessary detail crops, not just the montage. Confirm
figure axes/legends/panels, image aspect ratio, readable fonts, title/figure agreement,
citation placement, annotation placement, whitespace and excessive density. Read the notes.
Check that critical definitions precede results and that teaching examples are labelled.

## Projection readability

After examining details at useful magnification, inspect the actual PPTX's main slides
at the intended presentation size, with the whole page visible. Read the title, body,
navigation and load-bearing figure labels/numbers at that size. Detail zoom supports
source checking; it cannot excuse a main result that the audience cannot read. Check
the densest evidence page, longest title/body and smallest critical labels first to
catch a repeated layout problem, then review every page. A montage is for consistency,
not for approving small text.

On dense evidence pages, verify the visible row/column headers, baseline identities,
units, uncertainty notation and consequential conditions against full source context.
A caption-free crop can still lose SEM or the comparison that makes a number meaningful.
Keep key values and their decoding context legible together. If a full table fits only
as tiny print, move it to a true backup and use faithful, labelled original-image
excerpts with headers in the main deck; recheck the selection and context. Enlarge or
recompose the evidence panel before reducing native font roles. Check that long text
stays inside its content area and clears navigation, gutters, sources and page badges.
Important explanation cannot depend only on notes when the visible page is ambiguous.

Check exported native text for extra wrapping, isolated trailing characters and lines
that escape a frame even when the SVG checker passed. Compare the actual native text
frame with the planned content area and both script fonts. Repair at the backend's
supported authoring/export layer using its current instructions; do not default to
smaller fonts, remove scientific conditions or treat a valid SVG as evidence of a valid
PPTX. A changed export mode or font stack requires a fresh actual-PPTX render and
review of every affected page and recurring text role.

For default `academic_navigator` contracts, `review-init` seeds `projection_readability`
as pending on every page. Complete it with concrete observations from the final PPTX
render, including relevant evidence labels and the accepted role/exception of covers
or hidden backups. A backup may be denser than a main slide, but the intended Q&A
material still needs a usable reading view. Machine geometry/font checks, a source
crop inspected alone and approval of an earlier render cannot pass this check.

On the actual PPTX renders, check display crops against their full source context: the
paper's prose caption and adjacent text are removed unless explicitly requested, while
data legends, table headers, units and consequential conditions remain readable. Check
that explanations removed from the slide are present in notes or local evidence. Inspect
each native text role for the agreed family, size and weight across pages, and compare
emphasis colors with the limited palette. Theme/font statistics support this review;
they do not replace seeing the final rendered text. Source-figure lettering and recorded
cover/backup exceptions are reviewed separately.
For the default fonts, inspect both English and Chinese in the final render:
English uses Times New Roman and Chinese uses Microsoft YaHei, including navigation,
titles, annotations and page badges where applicable. Check for substitution and
mixed-language line reflow; a declared font stack alone does not prove either face
rendered correctly. Follow an accepted explicit font override instead when present.

When section navigation is enabled, check every applicable page for the same ordered,
consistently spaced top labels, the correct single active section, agreement with its `section_id`,
and clearance from the title and figures. The active fill should not gain a redundant
underline; do retain the separate body-title divider. A correct SVG strip can still shift or lose
fonts in PPTX export. Record these findings in the page's layout/reference review along
with any explicit exceptions.
For default `scope: "main_talk"`, compare the labels with visible non-exempt pages:
no label exists solely for hidden backups or an exempt cover. Hidden pages can omit
navigation or reuse an existing main section. Check actual whitespace between tabs
against the declared positive `tab_gap_px`, scaled for the canvas; an unbroken dense
bar fails this review even when all labels and colors are technically present.
For `width_mode: "content"`, compare the rendered tabs with the computed coordinates in the handoff.
Make sure that the group aligns with the title's left edge and each label has clear space on both sides.
The tabs must keep the same width and position across pages.
A short group stretched across the full width fails this review.
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
the handoff and then request backend changes. Own routine readability repair through
delivery: do not hand over a known tiny table, overflowing title or crowded page for
the user to rediscover. Record related defects together and request a coherent repair
batch rather than repeatedly changing isolated boxes. Keep previous versions.

After repair, rerender the actual new PPTX, inspect affected pages and compare recurring
elements across the deck. Independently review every final page before acceptance;
the production agent's claim or a first passing checker is insufficient. The same
agent can conduct a distinct review pass when no separate reviewer is available;
record the actual review mode honestly. For page splits/reordering, reconcile stable
slide IDs with physical order, navigation, page numbers, visible/hidden status, coverage
links, notes and the speaking budget before rebuilding the handoff and QA records.

Continue while a concrete repair can resolve the defects within the accepted scope.
If repeated local changes do not help, simplify the composition or change the evidence
selection with its context intact. Stop and explain an actual source, renderer or
scope limitation when no justified repair remains; label the affected deliverable
accordingly. No arbitrary retry count converts a failure to a pass, and routine repairs
within the accepted brief do not require another user confirmation.

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
