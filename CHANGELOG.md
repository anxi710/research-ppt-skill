# Changelog

## Unreleased

- Standardized the documented interpreter on Python 3.11, matching CI.
- Removed one-time GitHub repository publication and offline Git-history restoration
  helpers, their guide and tests. Routine repository checks and backend updates remain.
- Repository-root prompts use relative skill/material paths; the agent resolves them
  before changing directories. New PDF deliveries default to `<project-name>-preview.pdf`
  while existing workspace filenames and user overrides are preserved.
- Detailed, topic-centered research reports integrate supplied papers, notes and user
  results; type/depth choices survive intake and handoff while legacy briefs remain valid.
- Report planning and review cover explanatory depth, source synthesis, omissions and
  the split between timed main slides, detailed notes and hidden backups.
- Explicit parent intake before evidence preparation: resolve audience, purpose, time/Q&A,
  language, style, structure and deliverables, then capture actual acceptance or delegation.
- Pending intake snapshots and preflight/handoff checks prevent missing or stale brief
  confirmation; resumed work reuses accepted requirements and reconfirms material changes.
- Documentation uses direct recursive cloning as the standard setup and the current
  backend policy.
- Concise bilingual READMEs link to detailed first-use/maintenance guides, preserving
  each step's purpose, action and completion condition, and an agent environment setup reference.
- A pending synthetic `brief.json` example explains workspace locations, requirement
  fields and the confirmation lifecycle.
- Agents summarize default project names; initialization defaults to `outputs/<name>/`
  with collision suffixes, named delivery files and explicit destination overrides.

## 0.2.0

- General research presentation skill with explicit preparation/production/review boundaries.
- Current ppt-master through a real Git submodule; removal of the historical adapter.
- Evidence, figure, style and slide contracts plus immutable production handoff.
- Independent all-slide rendering, machine checks, pending review and repair workflow.
- Neutral configurable academic profile, synthetic fixtures and public-data safeguards.
- Maintenance/update/publication helpers and CI/Dependabot configuration.
