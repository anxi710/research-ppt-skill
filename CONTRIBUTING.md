# Contributing

Improve the research/preparation/review layer rather than duplicating ppt-master production.

For a bug, supply a synthetic minimal example, expected outcome, actual result, relevant
artifact/renderer versions and screenshots without private information. Reproduce the
failure in a test before changing a shared check. Content/style rules need a rationale
and a counterexample: avoid turning one paper's layout into a universal requirement.

Run `python -m unittest discover -s tests -v` and `python scripts/check_repo.py`.
Actual backend/rendering experiments must report what ran and what was not tested.

Do not commit user workspaces, source papers, paper images, logos, confidential results,
API credentials or font binaries. Preserve MIT notices and all separate dependency/asset
licenses. Submodule updates should be their own reviewable change, with observed
compatibility/limitation notes. Do not patch upstream integrity checks.
