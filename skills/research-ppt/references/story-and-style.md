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
Budget space for the accepted navigation, title, gutters and source/footer before
placing body copy or evidence. Prototype long titles and the densest evidence at the
intended presentation size; preserve usable margins instead of expanding text into
page chrome. The main argument must work without audience zooming or a full-table
backup being opened during the talk.

Specify the final `display_title` separately from `on_slide_text` (final body copy).
`question`, `topic`, `takeaway` and `reading_order` are planning metadata, not four more
things to print. Choose titles by page function: a topic for foundations, a numbered
question when it helps the argument, a supported finding for results. Read all display
titles together to check the talk's outline, then read each page aloud. Replace awkward
translations, metaphors and repeated disclaimers with direct explanations. Define a
technical term once and use a consistent Chinese/English form; keep established English
terms where the audience/reference uses them. Do not strengthen a finding while polishing.

Prefer affirmative metric definitions (what the axis measures) to repeated statements of
what it does not measure. Preserve consequential distinctions and experimental conditions.
Put full provenance and secondary caution in notes; the main reasoning must still be
understandable from the visible page. Do not shorten every page to the same number of labels.

By default, keep the cover limited to the talk/paper title and supplied metadata such
as presenter, occasion, date and source. Do not add
a background lesson, findings teaser or invented presenter information. Put the
necessary background on a separately planned content page and rebalance the time
budget; a cover is an explicit exception to the core-visual requirement. A different
opening format requires an explicit user choice or accepted replacement template.

For several passages on one page, group by meaning: stages, parallel comparisons,
observations versus implications, or a claim with its qualification. Use numbers for
an ordered argument and restrained frames or a shared panel for related text. Give
each group a short heading and enough separation to reveal the reading order. Record
the intended groups in the page plan; retain evidence qualifiers with their claim.
The default `content_grouping` policy records `enabled: true` and selected `treatments`
such as `cards` or `numbered_blocks`; it does not require the same group count on every page.
Define a small set of component classes: peer explanation cards share dimensions,
padding and edge treatment within each layout variant, including across pages. Edit or
split excess copy rather than enlarging an isolated card. Evidence frames and commentary
are different classes; preserve source-image aspect ratios rather than forcing every
container to match. Record minimum gutters and padding in the style profile. At
1280 × 720, start with 24–32 px between peer cards and scale with the canvas; keep a
clear gap after accounting for borders, shadows and text. Do not turn every sentence
into a separate card or surround a legible figure with decorative boxes. If groups
still feel crowded, simplify or split the page rather than squeeze the gutters.

## Style decisions

Unless the user supplies a different style or template, select the built-in synthetic
`assets/academic-navigator/` template workspace. Its defaults are a title-information cover,
separate background, coordinated navigation/title separator/page badge, semantic text
groups, body-only figures, fixed typography roles and one native emphasis color.
Record this basis in the project style profile; user overrides take precedence. The
defaults concern visual organization, not a fixed topic, chapter count or slide count.

New briefs record `design_contract_version: 1`; their style profile records
`design_contract: {version: 1, mode: "academic_navigator"}` for this default. Initialization
leaves a proposed template decision, not a completed application. Resolve it to a selected
template before preparation preflight; a `pending_default` decision or `applied: false`
cannot serve as evidence of backend use. Navigation starts enabled with no sections:
complete its ordered sections and each applicable page's `section_id` from the real talk.
Do not disable it merely to pass preflight with an unfinished plan.

Resolve the default workspace root from this skill's actual absolute directory, not from
the talk's working directory. Carry the exact root and an immutable template snapshot
through `production-handoff.md`. A template name or prose statement that the design was
inspired by Academic Navigator does not select or install its prototypes. The default
requires actual template application and the binding visual elements below; free layout
without importing the template system is not an equivalent default.

A user-selected replacement or explicit free-design choice records
`design_contract.mode: "user_override"` and an
`override` with `reason` and `user_instruction` grounded in the actual instruction or
accepted choice in the brief or intake response. Record which defaults it replaces.
A replacement follows the backend's current template workflow; the parent helper's
mandatory template packaging/application-record format applies only to the built-in
default. A genuine no-template choice needs no template snapshot or installation receipt.
A generic request to make a PPT,
an agent's aesthetic preference or a backend's free-design recommendation is not an
override. A different palette or suitable installed font does not by itself waive the
remaining navigation, cover, page-chrome and grouping requirements.

Inspect a selected template's rendered pages and explicit formatting at the backend's
allowed stage: candidate frontmatter first, full prototypes after selection and
installation when the current backend requires that order. Theme/master-inherited
fonts and colors may not appear in run-level statistics. Capture which decisions were
observed, user-required, or inferred. Reference aesthetics do not authorize reuse of
another presenter's identity, organization logo or confidential slide content.

Choose aspect ratio, typography, palette, source/footer convention and 3–5 compatible
layout patterns. Make academic visual density purposeful: enlarge the core visual,
arrange comparison panels, add only necessary annotations. Avoid big empty title-only
section dividers unless they serve the timing and narrative. Avoid copy-paste card grids.
Other bundled profiles remain selectable alternatives; none supplies a school identity.

For new work without an explicit font choice, use Times New Roman for English and
Microsoft YaHei for Chinese. Set `typography.font_family` and each default role's
`font_family` to `Times New Roman, Microsoft YaHei`, with
`latin_font_family: "Times New Roman"` and `cjk_font_family: "Microsoft YaHei"`.
The default Latin-first stack gives SVG/CSS previews the intended English face because
Microsoft YaHei also covers Latin characters. If the current backend resolves scripts
separately or needs an equivalent authoring realization, record its actual mapping and
any preview difference; verify the delivered PPTX's fonts and mixed-script line fit.
Stack order alone cannot prove the final fonts or safe textbox width.
Verify both fonts are available to the production
and rendering environments; do not silently substitute a different family. Existing
accepted project styles and explicit user font choices remain valid.

In `typography.roles`, define a small set of named roles with installed `font_family`,
`font_size_px` and agreed weight, such as title, body, annotation, navigation and footer. Keep each
role consistent across pages; a cover or backup exception must be explicit. Original
figure lettering is source content, not an invitation to vary native slide text.
Shorten copy, enlarge its area or split a page rather than shrinking one page's body
font to fit. Keep normal body text neutral and use a limited palette with one primary
emphasis color by default. Do not assign a new emphasis color to every method role,
box or keyword. Record native emphasis colors in `palette_policy.accent_colors` and
their maximum count in `palette_policy.max_accent_colors`. Preserve original data
colors and their meanings.

Use section navigation on body pages by default. Once the actual talk sections are
planned, record `section_navigation` in the style profile: enabled state, ordered
sections with stable IDs and short labels, applicable pages, placement, equal-sized
tab geometry, font role and inactive/active treatment. The default records
`scope: "main_talk"`: each listed section must have a visible, non-exempt content page.
Hidden backups do not create a separate chapter label. Record positive `tab_gap_px`;
start with 16 px at 1280 px canvas width (roughly 12–16 px is a useful starting range),
scale to the actual canvas, and confirm clear whitespace between tabs in the render.
Use separate equal-width tabs with visible gaps and no continuous backing rail.
Keep label spacing, baselines and active shape consistent; highlight exactly the
current section with the primary color. The active fill is sufficient: omit a second underline or indicator
under that tab by default. The separate line below the body title remains. Labels follow this talk's actual structure; do not
impose a fixed chapter sequence. Map each applicable page's `section_id` in the slide
plan to one of those IDs; a backup either names its section or has an explicit
navigation exception. A user-selected alternative may omit or replace the strip.
With navigation enabled, visible pages apply by default; record
cover/ending or other exceptions in `exempt_slide_ids`. Hidden pages may omit the strip
and `section_id`; any supplied ID must still name an existing main-talk section.
Reserve the strip's area so it does
not compete with the title.

Treat recurring navigation, title separator and page numbering as one `page_chrome`
system. Record their geometry, applicable page types and exceptions in the style
profile. By default, place the separator below the content title at a common
position and keep a current-page-only number in a small background badge at the lower
right. Count all physical pages, including the cover and backups, in one continuous
sequence unless explicitly overridden; do not switch to a total-page fraction. Keep
the badge clear of sources and data. A title-only cover can omit body navigation and the title rule
without losing the shared typography and palette.
The default policy uses `cover: {slide_ids: [...], title_information_only: true}`,
`page_number: {format: "current", position: "bottom_right", background: true}` and
`title_separator: {enabled: true}`. New workspaces receive page-chrome and content-grouping
policies; initialization does not complete intake or approve their rendering. Cover IDs
identify visible pages in the plan. Geometry, page-type exceptions and the numbering
convention remain explicit design decisions.

`assets/academic-navigator/` supplies the reusable synthetic template workspace for this
default. A user can replace its palette, sections or template without losing
the evidence requirements. It is not a mandatory chapter list, page count or scientific
structure. Read the current backend's template contract and supported route before reuse;
follow its selection, validation and installation sequence rather than treating bundled
assets as an automatic importer. After installation, derive a concrete application plan
from the project-local prototypes: record what persists, how page roles map to available
prototypes, and any required layout adaptation. Even if the backend permits style-only or
flat reuse, the default retains the binding information-only cover, separate background,
single-highlight navigation, body-title divider, current-page badge, typography/palette
roles and consistent peer grouping. Changing the backend's internal reuse scope does not
waive them. Adapt section labels and content to the accepted talk, and validate actual
PPTX renders rather than assuming template installation proves its visual application.

When a user supplies their edited final deck, treat it as stronger style evidence than a
generic profile. Read `references/reference-calibration.md` for pairwise analysis. Record
observations in `style_profile.json`: reference slide numbers, title/body/caption sizes,
figure footprint, whitespace, alignment, terminology, citation placement and opening/
closing/backup choices. Distinguish observed rules, explicit requirements and assumptions.
Keep identities and source material in the private project, not in a public skill profile.

New plans use `communication_contract` v1 in the style profile (see its template): final
display titles, citation placement and a small set of concrete acceptance rules. The helper
requires separate audience-copy/reference-match reviews for this contract; it cannot judge
the prose or reference match itself. Legacy workspaces without it remain supported.
`citation_placement` is `compact_footer`, `notes`, or `per_slide`. For `per_slide`, every page
records its own `citation_placement` as `compact_footer` or `notes`. `on_slide_text` is an
explicit list of nonempty strings; use `[]` for a page with no body copy. Respect a user's
clean-body reference: bibliography can live in
notes, while necessary figure labels, conditions and disclosures remain visible. A legacy
`source_footer` flag does not override the explicit communication contract.

Prototype the opening, a foundation/mechanism page and a dense results page in the backend's
allowed workflow. Evaluate figure legibility and natural wording at presentation size before
expanding. Reuse the accepted page patterns; do not infer that larger fonts or fewer words
are improvements when the user's reference already keeps the body composition intact.

## Figure handling

Actively consider relevant primary-source images for necessary background and benchmark
pages, including when the supplied paper has no suitable image. Prefer the benchmark's
original paper, official project/task documentation or original dataset page; select a
real task scene or explanatory figure that teaches the agreed concept. Search only for
the required context, respecting explicit source-only, offline and no-web limits. A
single-paper talk can use this contextual visual sourcing without becoming a literature
review; it does not authorize new result claims or replacing the supplied paper version.

Read the original page and inspect the actual image before use. Register its original
URL, title/author, version/date, figure/page locator, retrieval date and local file/hash
in the private source/figure inventory. Retain the available attribution/usage terms.
Mark its role as external context/illustration, distinguish its benchmark version from
the focal experiment and carry a concise source label plus full locator in notes. Do
not imply that it depicts the focal paper's experiment. Use original image pixels and
faithful crops; do not redraw or generate a lookalike of published evidence. If no
suitable retrievable image exists, use a clearly labelled native teaching schematic or
record the gap, rather than adding unrelated visual filler.

Use `figure_manifest.example.json` for provenance. Original crop coordinates use the
visible unrotated PDF page, top-left origin, PDF points. Check rotations and nonstandard
page boxes; normalize a separate copy and update provenance when necessary. Never infer
crop coordinates from unknown-resolution previews. Preserve original colors and scale.

The presentation asset normally contains only the figure/table body. Remove the paper's
Figure/Table number and descriptive caption, adjacent prose, cross-page text and outer
whitespace; do not paste their long explanations into slide copy. Preserve the full
caption and original page/context image separately in local evidence, and carry the
explanation and full locator into notes. A concise native source locator or panel label
may remain according to the citation policy. An explicit user request can retain a caption.
Record the default as `figure_policy: {display_region: "body_only", caption_policy:
"notes_only"}`. In each original figure/table record, the verified `path`/`sha256`
identify its display crop; `context` retains the original context image and provenance,
and `caption_provenance` retains the caption text and locator. These records support
inspection; a policy string cannot prove that a crop excluded the caption.

Distinguish a prose caption from a data legend. Keep decoding information: axes, units,
series/color/symbol legends, panel labels, table headers, footnote markers and uncertainty.
Retain consequential metric definitions or statistical/experimental conditions from a
caption on the slide as concise native text when the image would otherwise be misleading;
notes alone cannot replace those conditions. If a shared legend is separate, bind it to
the panels in the plan. Check both the display crop and full context before marking the
asset verified, including when extraction supplied the image automatically. Avoid
decorative icons drawn over data.
For a dense source table, select a faithful crop of the rows/columns needed for this
page's comparison and keep their original headers, method/baseline labels and decoding
context attached. Several labelled original-image excerpts may form one coherent
comparison; disclose selection and keep full context/provenance in local evidence.
Retain uncertainty notation (for example SEM), units and consequential conditions on
the page when they determine the reading. Do not silently replace a cropped-away
baseline with a native claim or enlarge a column without its header. Put the complete
table in a true backup when useful. Prefer a wider evidence panel, a separate setup
page or a split comparison to shrinking the whole table into a narrow commentary
layout. Judge the rendered critical values and labels rather than imposing one
absolute font-size threshold on all source figures.
Use native editable labels and explanatory diagrams, but do not claim a raster plot has
editable source data. An accessibility description belongs in the asset inventory/notes.

For a conceptual scene that benefits from raster illustration, modest image generation
is another option; follow `image-generation.md`. Match the accepted palette and visual
style, keep text as native slide labels, register `kind: generated_concept`, and preserve
the prompt, actual tool/model and output provenance. It is an illustration, not a source
figure or measured result. Choose among source images, native diagrams and generation
by teaching value; neither external search nor generation is mandatory on every page.

## Exit review

Every visible content page has a question, core visual, source links, notes and duration;
the title-only cover retains its explicit role and metadata constraints. Main
conclusions receive more time than routine setup; detailed proof/ablation/Q&A material
can become real hidden backup slides. Summed durations are planning estimates only.
Compare the deck and notes with the accepted scope and coverage list. Are the important
questions explained, not merely named? Do the sources form a connected argument? Are
omissions and evidence gaps visible? Detailed coverage is a judgment, not a slide count.
