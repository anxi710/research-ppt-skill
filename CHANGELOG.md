# Changelog

Skill versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current version is recorded in [SKILL.md](skills/research-ppt/SKILL.md)'s
`metadata.version`; release preparation is described in [Contributing](CONTRIBUTING.md#versioning).

## Unreleased

Changes after 0.3.0 will be collected here.

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
