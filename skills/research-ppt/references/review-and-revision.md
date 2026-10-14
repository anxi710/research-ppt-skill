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
source footer, annotation placement, whitespace and excessive density. Read the notes.
Check that critical definitions precede results and that teaching examples are labelled.

## Scientific review

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
Record editable/raster elements and font requirements; never redistribute font binaries.

A skill release must not include the private talk's PDFs, original images, institution logos,
unpublished data, personal identities or secrets. Generalize lessons into rules and synthetic
fixtures. Permission to create a public skill repository does not imply permission to publish
all inputs used by that skill.
