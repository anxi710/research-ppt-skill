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

## Versioning

Use [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html): `MAJOR.MINOR.PATCH`.
The skill's public interface includes its documented workflows, helper CLI options,
workspace formats and compatibility with saved briefs and review records.

| Increment | Use for |
|---|---|
| PATCH | Compatible fixes and documentation corrections that preserve the interface. |
| MINOR | New compatible workflows, capabilities or optional record fields. |
| MAJOR | Incompatible changes to the public interface after 1.0.0. |

During `0.y.z` development, incompatible changes increment MINOR and include migration
notes; compatible fixes increment PATCH. Use `1.0.0` when the public interface is stable.
Python and ppt-master versions are separate from the skill version.

Collect routine changes under `Unreleased` without changing the version on every commit.
When preparing a version, preview the change and then apply it:

```bash
python scripts/bump_version.py minor --dry-run
python scripts/bump_version.py minor
```

Choose `patch`, `minor`, `major`, or an exact version such as `1.0.0-rc.1`.
Named increments increase the selected core number, reset lower numbers and remove
prerelease/build suffixes. An exact version must have greater SemVer precedence than
the current version; changing build metadata alone does not increase precedence.
Use `--date YYYY-MM-DD` to override today's changelog date, or `--root PATH` to target
another checkout. `--dry-run` shows a unified diff without writing files.

The script updates `metadata.version` in `skills/research-ppt/SKILL.md` (the canonical
version) and existing README Skill badge labels and URLs. It moves `Unreleased`
entries into a dated version section, preserves older entries and leaves a fresh
`Unreleased` section. It does not commit, tag or push.

After updating the version:

1. Run the required checks above. `check_repo.py` validates SemVer and agreement
   between the skill metadata, README badge and latest numbered changelog section.
2. Commit the versioned state before creating a matching `vX.Y.Z` Git tag when a
   release is requested. A changelog entry alone does not create a tag or GitHub Release.

Once a tagged version is released, record further changes in a new version rather
than moving the existing tag.
