# Audience, story, style and visual assets

## Adapt the narrative to the research type

Integrated research report: research question → necessary background → organizing
framework/methods → evidence across materials → comparisons and analysis → limitations
and supported implications. Connect the user's progress and proposed next steps when
the request and materials support them. Select relevant sections, not a mandatory
chapter template; do not invent original contributions or experiments to fill a section.
Empirical paper: phenomenon → hypotheses → controlled setup → evidence → scope.
Method paper: limitation → design idea → mechanism → comparisons/ablations → analysis.
Theory paper: definitions → motivating example → assumptions → result → intuition → limits.
Review: organizing question → taxonomy → evidence across sources → agreement/conflict → agenda.
Progress report: objective → work done → evidence → failure diagnosis → next decisions.

Use the user's requested structure when explicit. Add only the foundations needed by this
audience, usually a concrete task example, an interaction/model diagram and the evaluation
unit. Do not spend five slides explaining AI to AI researchers.

## Synthesize materials and control depth

Organize a report by questions, mechanisms, evidence or project decisions, not by the
order files arrived. Use a common set of comparison dimensions where defensible.
Cross-source agreement, disagreement and missing evidence each have a place; preserve
which observations are published, the user's own results or presenter analysis. Multiple
sources need not appear on every page, but their roles should form one coherent story.
Explicit single-paper talks remain valid and do not require outside sources.

`detail_level` specifies explanation depth, not text density. `overview` emphasizes the
central question and strongest evidence; `standard` adds enough method and evaluation
detail to follow the argument; `detailed` explains needed definitions/assumptions, the
method's mechanism, experimental setup, key results, comparisons, uncertainty and
limitations when supported. Include transitions and sufficient speaker notes to teach
the material, rather than converting headings or an abstract into a finished report.

For detailed or multi-material reports, keep a compact `coverage` list alongside `slides`
in `design/slide_plan.json`. For each required topic, record supporting source IDs,
slide IDs or the relevant notes, and whether it is in the main deck, backups, notes,
deliberately excluded or blocked by a source gap. Give reasons for exclusions/gaps.
This is an editorial review aid carried in the immutable handoff, not an automatic
certificate of completeness. An irrelevant supplied file can be excluded with a reason;
do not add slides merely to cite every file.

Budget main slides against agreed speaking time after reserved Q&A. Keep the reasoning
needed to understand a conclusion in the main deck; place detailed derivations, additional
ablations/data tables and optional examples in notes or genuinely hidden backups.
If must-cover content still exceeds the budget, negotiate scope or duration. Do not
silently omit it, shrink fonts or promise a detailed talk in an implausible time.

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
Compare the deck and notes with the accepted scope and coverage list. Are the important
questions explained, not merely named? Do the sources form a connected argument? Are
omissions and evidence gaps visible? Detailed coverage is a judgment, not a slide count.
