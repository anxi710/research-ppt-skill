# Upstream integration and update policy

## Actual submodule

`.gitmodules` associates `third_party/ppt-master` with the upstream public Git repository
and tracking branch `main`. The parent tree contains a mode-160000 gitlink, not a directory
of copied source or only a text URL. Git's model records a commit for every parent snapshot.
See [git-submodule](https://git-scm.com/docs/git-submodule).

A normal `git submodule update --init` restores the recorded snapshot; `--remote` fetches
and uses the configured branch. New jobs use `python scripts/upstream.py update`, which
updates from the branch and refuses dirty/local unrecorded work rather than discarding it.
The helper does not commit or push. Maintainers commit an accepted updated gitlink.

## Current does not mean uncontrolled

- Before a new job: fetch the current branch, inspect current entry instructions and license,
  check representative slides, and record the actual revision.
- During a job: do not mutate the backend under an ongoing generation/review.
- Reproduction: use the recorded backend revision from that job.
- Upgrade: create a new run and review, rather than modifying the past record.

The submodule tracks upstream `main`, while every job records the actual commit it uses.
A detached HEAD in a submodule is normal: Git records a commit even when updates follow a
branch. A network failure means the latest revision is unknown, not verified.

## License and capabilities

The helper checks that the current root LICENSE resembles MIT and discovers existing
entry files. That is a conservative change signal, not a legal audit or execution test.
If upstream reorganizes its directories, consult its current README/AGENTS rather than
inventing commands. If the license changes, stop and review compatibility. Upstream's
own integrity, attribution, confirmation and technical gates remain intact.

The prep/review interface is provider-independent. Another backend can be supported by
adapting the handoff and receipt, but do not silently switch when the user asked for ppt-master.

## Dependency PRs

`.github/dependabot.yml` configures Git-submodule update PRs on workdays and Actions updates
weekly. Repository settings, permissions and GitHub service behavior still apply. The
configuration alone is not proof that PRs were created. No automatic merge is enabled.
See [Dependabot options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).

CI does not execute upstream code on untrusted PRs; its default checks are our own synthetic
tests and static repository checks. Test an updated backend in an appropriate sandbox before
accepting a real production job. Document compatibility observations without claiming a
complete test of the entire upstream project.
