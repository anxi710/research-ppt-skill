# Changelog

Skill versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current version is recorded in [SKILL.md](skills/research-ppt/SKILL.md)'s
`metadata.version`; release preparation is described in [Contributing](CONTRIBUTING.md#versioning).

## Unreleased

### Tests

- Run the opt-in real PPTX render tests in a separate Linux CI job with LibreOffice
  and open fallback fonts; an explicitly requested render run fails if the renderer
  is missing. Retain synthetic PDFs, PNGs, reports and logs for inspection.
- Extend synthetic rendering coverage to mixed Chinese/English text, main-section
  labels, interleaved hidden backups, page order and output fingerprints. This is
  helper-path regression coverage, not backend template or visual-quality acceptance.

## 0.4.2 - 2026-10-16

### Documentation

- Add concise API image-generation setup to both READMEs, distinguish available
  built-in/tools from external-service setup, and clarify environment inheritance
  and the separate image-model parameter.

## 0.4.1 - 2026-10-16

### Fixed

- Default English text uses Times New Roman and Chinese text uses Microsoft YaHei
  throughout role-level style data, reusable templates, handoff and rendered review.
- Default navigation lists main-talk sections only, with visible gaps between
  equal-width tabs; hidden backups do not become navigation parts.
- Projection-readability review is required for the default contract. Dense evidence
  pages use readable, faithful excerpts with metric keys; actual-PPTX review and
  repair finish before delivery, including roster/notes consistency after replanning.
- New workspaces require a resolved design contract: planned section navigation,
  complete default visual policies and an explicit template decision. A different
  user-requested style is recorded as an override; legacy workspaces remain supported.
- Default template assets now travel in the immutable handoff with exact paths and
  fingerprints. Acceptance checks require installed-template provenance and independent
  rendered-page review, preventing a style-name-only free-design fallback.

## 0.4.0 - 2026-10-15

### Added

- A repository `bump_version.py` helper previews or applies SemVer increments while
  synchronizing skill metadata, README badges and dated changelog entries.
- Figure framing keeps paper captions in notes and verifiable local context while
  preserving the data, axes, units and series legends in displayed crops.
- Default section navigation, fixed typography roles and a limited accent palette
  travel through preparation and handoff into pending, per-slide visual review.
- A reusable, synthetic Academic Navigator template provides information covers,
  numbered explanations, evidence panels and synthesis pages. Cover separation,
  title rules, current-page badges and semantic grouping have explicit review checks.
- Background and benchmark pages can source attributed primary-source context images
  beyond supplied materials, respecting explicit source/browsing limits and claim scope.
- Optional concept-image generation keeps style and provenance separate from evidence;
  a setup guide covers available Codex tools, Claude Code integration and the Image API.

### Fixed

- PPTX inspection counts editable text inside nested shape groups.
- Default navigation uses one active fill; peer cards keep consistent geometry/padding
  and clear gutters across pages while image frames preserve source aspect ratios.

## 0.3.0 - 2026-10-15

### Added

- Detailed research reports integrate supplied papers, notes and user results around
  a research question. Type/depth choices and mixed-source provenance survive intake
  and handoff; legacy briefs remain valid.
- Parent intake resolves audience, purpose, time/Q&A, language, style, structure and
  deliverables. Pending or stale confirmation blocks preparation and production handoff.
- Report planning and review cover explanatory depth, synthesis, gaps, timed main
  slides, detailed notes and hidden backups.
- Calibration against user-edited decks records reusable communication requirements,
  including display titles, slide text, citation placement and per-slide review.
- Agents summarize project names; initialization creates private `outputs/<name>/`
  workspaces with collision suffixes and explicit destination overrides.
- Bilingual first-use/maintenance guides, an agent environment guide and a pending
  `brief.json` example explain each step and its completion criteria.
- README badges show the skill version, Python version, CI status and license.
  Repository checks enforce version consistency with the skill metadata and changelog.

### Changed

- Documentation specifies Python 3.11 and direct recursive cloning. Repository-root
  prompts accept relative skill/material paths, resolved before directory changes.
- New PDF deliveries default to `<project-name>-preview.pdf`; existing workspace
  filenames and explicit overrides are preserved.
- CI uses `actions/checkout@v7` and `actions/setup-python@v7`.

### Removed

- One-time GitHub publication and offline Git-history restoration helpers, their
  guide and tests. Routine repository checks and backend updates remain available.

## 0.2.0

- General research presentation skill with explicit preparation/production/review boundaries.
- Current ppt-master through a real Git submodule; removal of the historical adapter.
- Evidence, figure, style and slide contracts plus immutable production handoff.
- Independent all-slide rendering, machine checks, pending review and repair workflow.
- Neutral configurable academic profile, synthetic fixtures and public-data safeguards.
- Maintenance/update/publication helpers and CI/Dependabot configuration.
