# Learn from a user's edited final deck

Use when the user supplies a generated deck and its edited final version, or asks to
follow a previously used deck. This is analysis and style preparation, not a new talk
intake or permission to change the originals. Keep comparisons in the private workspace.

## Compare what actually changed

For a generated/final pair, render both PPTXs and align pages by content, not just slide
number. For a single reference, inspect its pages without requiring a second deck. Inventory native
text, formulas, image hashes, bounding boxes, hidden flags and speaker notes. Inspect
the rendered pairs. Record added/deleted/reordered pages separately from local edits;
exclude deleted backups and rewritten covers from body-density comparisons.

Use a short change table: page pair, observed edit, likely intent, reusable rule, and
confidence. Distinguish repeated preferences from one-off fixes, new source material,
personal metadata, editor side effects and changes to research claims. Do not infer a
new evidence rule from a stylistic edit or strengthen a finding to match casual wording.

Common useful distinctions:

- A paper-focused title page versus a results teaser: follow the chosen talk format;
  copy neither old presenter identities nor a possibly inaccurate translated title.
- A concrete task illustration versus a text-only example: label an illustration as
  illustrative, register its source and avoid implying it is this paper's experiment.
  New material in the edited deck was not necessarily available during the first build.
- Bibliographic footers versus experimental conditions: a clean reference may move
  bibliography to notes; axes, metrics and consequential qualifiers stay on the page.
- Paper captions versus data legends: remove surrounding prose when adapting an original
  figure/table, but retain the decoding legend and consequential conditions. Keep the full
  caption and source-page context in local evidence and notes.
- Natural terminology versus rhetorical padding: keep audience-recognized terms,
  affirmative definitions and concise findings. Do not require every page to disclaim
  all possible misreadings after the distinction has already been taught.
- Formula typesetting versus new mathematics: use supported equation objects or
  editable mathematical typography, then inspect rendered subscripts, superscripts,
  symbols and indices. A transcription/index error is a content defect, not style.
- Fewer total pages versus less technical depth: removing hidden backups does not
  imply the user wants shorter explanations in main slides. Record backup/closing policy.

## Measure fairly

Compare title, body, caption and footer separately. Weight font statistics by characters
or text areas, not by run counts: manual editors frequently split one phrase into many
runs. Inspect inherited theme fonts and native math, which may be absent from `a:t`.
Check image identity before calling a figure replaced; inspect dimensions before
claiming the user enlarged it. Deleting a long footer may explain almost all text loss.

A final deck is evidence of the user's intent, not a technical gold standard. A target
editor may preserve unsupported objects while another renderer wraps text differently.
Record the renderer and actual symptoms; do not call incidental clipping or lost notes
a preference. Recheck title fit and formulas after font changes or manual saves.

## Convert the observations into production constraints

Keep a project-local style profile with reference page numbers and observed measurements.
Translate repeated edits into a small `communication_contract.rules` list and set
`citation_placement` to `compact_footer`, `notes`, or `per_slide`. In the last case,
record each page's placement in its plan. Record terminology and opening/closing/backup
choices alongside it. Mark inference as inference; preserve explicit user requirements.
If the reference uses top section tabs, record their order, geometry, active treatment
and applicable page types, then map the new talk's own sections to them. Extract font
roles and a limited emphasis palette across representative pages; do not copy individual
page font changes or method-role colors without a reason. Use one active navigation
fill without a redundant underline unless a user selects that treatment.
Inspect the opening separately: a title-only cover is a page-role choice, not evidence
that background should disappear. Record navigation, title rules and page-number badges
together as page chrome, including the current-page convention and cover/backup exceptions.
Distinguish meaningful numbered/grouped passages from decorative boxes; transfer the
reading hierarchy rather than mechanically putting every paragraph in a card. Compare
peer box dimensions, padding and gutters across pages; isolate legitimate image-frame
variants from accidental oversized commentary cards.

Use final `display_title` and `on_slide_text` in the page plan. Prototype representative
opening, explanation and dense-results pages through the current backend before expanding.
Review both audience copy and reference match on real PPTX renders. Keep detailed notes
and source locators even if the edited reference lost its notes during a manual save.

Publish only generalized workflow changes and synthetic regression tests. Do not put
the private reference, screenshots, paper content, names or institutional assets into
the distributable skill. Promote a preference into skill defaults only when the user
explicitly asks to do so, as with the built-in academic-navigator research style;
retain clear user overrides and generalize its assets with synthetic content.
