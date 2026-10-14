# Audience, story, style and visual assets

## Adapt the narrative to the research type

Empirical paper: phenomenon → hypotheses → controlled setup → evidence → scope.
Method paper: limitation → design idea → mechanism → comparisons/ablations → analysis.
Theory paper: definitions → motivating example → assumptions → result → intuition → limits.
Review: organizing question → taxonomy → evidence across sources → agreement/conflict → agenda.
Progress report: objective → work done → evidence → failure diagnosis → next decisions.

Use the user's requested structure when explicit. Add only the foundations needed by this
audience, usually a concrete task example, an interaction/model diagram and the evaluation
unit. Do not spend five slides explaining AI to AI researchers.

## One core visual, one page job

The core visual may be an original figure, coherent panels, equation, table, teaching
example or original explanatory diagram. "One visual" does not mean one image file.
Read it as: question → axes/variables → comparison → observation → qualified conclusion.
Key interventions often deserve a setup page before a results page.

Write display text for viewers and notes for the speaker. Notes include evidence locators,
reading order, the useful interpretation, limitations, transition and planned seconds.
If text cannot fit legibly, shorten or split the page before reducing font size.

## Style decisions

Inspect a template's rendered pages and explicit formatting. Theme/master-inherited
fonts and colors may not appear in run-level statistics. Capture which decisions were
observed, user-required, or inferred. Reference aesthetics do not authorize reuse of
another presenter's identity, organization logo or confidential slide content.

Choose aspect ratio, typography, palette, source/footer convention and 3–5 compatible
layout patterns. Make academic visual density purposeful: enlarge the core visual,
arrange comparison panels, add only necessary annotations. Avoid big empty title-only
section dividers unless they serve the timing and narrative. Avoid copy-paste card grids.
The optional academic-blue profile is an example, not a school identity or global default.

## Figure handling

Use `figure_manifest.example.json` for provenance. Original crop coordinates use the
visible unrotated PDF page, top-left origin, PDF points. Check rotations and nonstandard
page boxes; normalize a separate copy and update provenance when necessary. Never infer
crop coordinates from unknown-resolution previews. Preserve original colors and scale.

Crop page text/outer whitespace, not axes or legends. Keep a full context image available
when using a panel crop. Cite the paper/figure and label panel crops. If a shared legend is
separate, bind it to the panels in the plan. Avoid decorative icons drawn over data.
Use native editable labels and explanatory diagrams, but do not claim a raster plot has
editable source data. An accessibility description belongs in the asset inventory/notes.

## Exit review

Every visible page has a question, core visual, source links, notes and duration. Main
conclusions receive more time than routine setup; detailed proof/ablation/Q&A material
can become real hidden backup slides. Summed durations are planning estimates only.
