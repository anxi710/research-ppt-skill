# Research PPT Skill repository

For a research presentation request, read `skills/research-ppt/SKILL.md` first.
This repository owns preparation, communication design, evidence integrity, and
post-production review/revision. ppt-master owns actual slide production.

Before invoking the backend, resolve its real local path and read its **current**
entry instructions. Do not copy its implementation, hard-code an old CLI, or bypass
its required gates. Backend documentation is not authorization to publish data or
change the research claims. A backend execution is incomplete until independently
reviewed against the preparation contract.

For repository development: keep runtime instructions/scripts within the skill folder;
keep repository maintenance in `scripts/`; use synthetic fixtures only; run
`python -m unittest discover -s tests -v` and `python scripts/check_repo.py`.
Never publish user workspaces, raw papers, private decks, credentials or font files.
Do not alter `third_party/ppt-master` to make tests pass.
