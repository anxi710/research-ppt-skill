---
deck_id: academic-navigator
kind: deck
category: scenario
summary: Research group presentations with an information-only cover, visible topic navigation, and grouped explanations alongside source evidence.
keywords: [research, navigation, evidence, numbered-groups]
primary_color: "#2F5597"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
replication_mode: standard
native_structure_mode: structured
page_count: 4
placeholders:
  01_cover: ["{{TITLE}}", "{{SUBTITLE}}", "{{AUTHOR}}", "{{DATE}}"]
  02a_content_numbered: ["{{PAGE_TITLE}}", "{{CONTENT_AREA}}", "{{BLOCK_2}}", "{{BLOCK_3}}", "{{SOURCE}}"]
  02b_content_evidence: ["{{PAGE_TITLE}}", "{{CONTENT_AREA}}", "{{SIDE_NOTE_1}}", "{{SIDE_NOTE_2}}", "{{SOURCE}}"]
  03_ending: ["{{PAGE_TITLE}}", "{{CONTENT_AREA}}", "{{SOURCE}}"]
---

# Academic Navigator — Design Specification

## I. Template Overview

A reusable starting point for projected research group presentations. Typical readers are students and researchers who need to distinguish background, a research problem, mechanisms, measured evidence and scoped conclusions. The four prototypes represent title information, numbered explanations, evidence with reading guidance, and a concise synthesis; they describe available compositions rather than a future talk's required order or page count. All example content is synthetic. There is no institution, speaker identity, logo, paper image or font binary.

Creation basis: direct user instructions and delegated design choices, not a source-deck topology. One newly authored Master owns the neutral field and page badge; four distinct Layouts own the title/metadata, three stacked groups, evidence/side notes, or synthesis slot geometry. No chapter divider prototype is included because the requested recurrence is a content navigation strip rather than extra separator pages.

## II. Color Scheme

| Role | Value |
|---|---|
| Emphasis and active navigation | #2F5597 |
| Body | #1E293B |
| Secondary | #526275 |
| Background | #FFFFFF |
| Navigation and grouped surfaces | #EDF3FA |
| Hairline | #D6E0EA |

Native emphasis uses one blue. Original evidence images retain their source encoding. Boundaries communicate grouping; they do not give every paragraph a separate competing accent.

## III. Typography

Latin Arial, Chinese Microsoft YaHei; no font embedding. Cover title 56px, content title 40px, body/subheading 32px, annotation 24px, navigation 18px, source/footer 16px. Use bold within the same role for labels and results, rather than inventing page-specific font sizes. Native figure lettering is outside these roles. Downstream planning resolves final type sizes against actual content.

## IV. Signature Design Elements

- The information cover contains the title, subtitle and supplied bibliographic/presentation metadata, with a slim blue left rail and a quiet metadata field. It has no background explanation, mechanism, results, or section-navigation row.
- Content headers reserve y20–62 for a connected rounded navigation rail, y80–130 for the title, and y145 for a pale horizontal divider with a short blue leading segment. The body begins at y164. Example topic labels are only a demonstration: replace them from the downstream plan's ordered sections and derive exactly one active segment from section_id. Covers are exempt.
- Navigation uses five evenly spaced example segments within x48–758: a pale shared field, 01–05 order cues, a blue active segment without an additional active underline. The same group is adapted to a different section count instead of squeezing longer labels.
- The lower-right snipped-corner blue badge occupies x1164/y674/w68/h36; its white editable number shows only the current physical slide number. It never shows a total, fraction or letter-only backup code. A separate subtle backup mark may appear near the header.
- Numbered text groups share a left number gutter and restrained pale/outline panels. A number distinguishes a topic or step, not an implied ranking; replace with semantic labels when order is not meaningful. Evidence pages keep the source figure separate from short, visibly grouped notes, with no prose caption baked into the image.
- Page-scale geometry signatures: cover → identity and metadata field → slim rail; explanation → three semantic rows → numbered insets; evidence → wide source field and narrow reading rail → quiet outline plus grouped notes; synthesis → one shared field → three internal rows. The strongest rejected alternative was a repeated equal-card grid on every page: it would falsely flatten evidence and commentary into peers.
- Peer panels use equal geometry, padding and edges within each semantic class. Numbered panels are three 1184×144 rows with 24px gaps. Evidence note panels are two 408×232 regions with a 24px gap and 20px insets; the separate 752×488 evidence region preserves source aspect ratio. Context imagery may come from attributed primary sources; generated concept art remains optional and is never evidence.

## V. Page Roster

| File | Role / Layout picker | Slots and capacity |
|---|---|---|
| `01_cover.svg` | Information cover / Information cover | title 96 202 1088 82; subtitle 96 314 1088 108; author 116 530 790 44; date 116 586 790 36; page-number 1172 680 52 26. Title/subtitle left-aligned, no scientific body content. |
| `02a_content_numbered.svg` | Explanation / Numbered explanation | title 48 82 1184 52; body indices 1–3 at x126, y184/352/520, each 1086×104; footer 48 675 1080 30; page-number 1172 680 52 26. Each body slot begins upper-left and fits up to two short 32px lines; notes carry detail. |
| `02b_content_evidence.svg` | Source evidence / Evidence with notes | title 48 82 1184 52; object evidence 68 184 712 448; body1 at 844 184 368 192, body2 at 844 440 368 192; footer 48 675 1080 30; page-number 1172 680 52 26. Evidence slot preserves source aspect ratio; annotation groups stay outside it. |
| `03_ending.svg` | Synthesis / Three-part synthesis | title48 82 1184 52; body126 194 1060 410; footer48 675 1080 30; page-number1172 680 52 26. One shared plane with three visual rows; not a fixed thank-you page. |

## VII. Placeholder Overrides

The frontmatter records extra semantic body slots for the numbered and evidence variants. Navigation labels are Slide-local examples, not inherited identity or a mandatory five-section outline. All body/object text carriers start at the upper-left of their full reusable frame. The number badge is a short focal exception: its carrier is centered.

The slide-number carrier uses the prototype ordinal as its visible sample and explicit semantic slide-number binding; it compiles as a native current-slide field. Downstream authors set the carrier to the actual output ordinal rather than preserving this sample.
