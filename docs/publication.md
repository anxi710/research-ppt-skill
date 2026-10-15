# Creating the public GitHub repository

Use `git clone --recurse-submodules <repository-url>` to obtain the repository.
This guide covers creating a new public GitHub repository and maintaining it.
Run publication in an authenticated environment that supports GitHub writes;
local files and configuration alone do not establish remote publication.

## Create a new public repository

The initial publisher requires a clean local Git repository with no configured remote
and a new repository name. A clone normally already has an `origin` remote; use the
normal review and push workflow for that repository. The initial publisher is for a
separate, reviewed local repository intended for first publication.

```bash
python -m pip install -r requirements.txt
gh auth login
python scripts/publish_github.py --repo research-ppt-skill --publish
```

The publisher performs a public-file heuristic check, refuses dirty work/unexpected
remotes, verifies the authenticated personal account, refuses an existing repository,
updates the submodule to the configured current branch, runs tests, creates a **public**
repository, pushes, then verifies public visibility and remote `main` commit equality.
It does not request/paste tokens, overwrite a repository, force-push, or stage arbitrary
workspace files. With `--owner`, it requires the login to match; organization publishing
is intentionally not inferred. Without `--publish`, it only prints the plan.

If your network disallows GitHub or authentication is missing, the operation stops.
If creation succeeds but a push fails, inspect the returned error and remote state;
do not blindly rerun to create a second repository. For an existing newly created empty
repository, verify ownership/visibility and use an ordinary non-force push intentionally.
Never interpret a nonzero result as proof that nothing was created.

## Maintenance

After review of a dependency update:

```bash
python scripts/upstream.py update
# Read current upstream instructions and inspect changes.
git diff --submodule=log
git add third_party/ppt-master
git commit -m "chore: update ppt-master backend"
git push
```

Dependabot proposes updates according to `.github/dependabot.yml`; it does not merge them.
CI configuration executes only after GitHub accepts it and relevant repository settings
permit it. Adding the files locally does not start an automation or prove a CI pass.

The public repository should contain only original generic skill files and licensed
submodule metadata. GitHub's root license detection is not a license audit of every
runtime dependency, paper, figure, template or font used in a private talk.

## Optional Git metadata recovery

If a standalone local copy has no Git metadata but includes `research-ppt-skill.bundle`,
`python scripts/restore_git.py` can restore its parent history and submodule gitlink.
Existing working files are preserved, and upstream source is fetched separately.
This recovery tool is not part of setup for a normal Git clone.

Official command references:
[GitHub CLI repo create](https://cli.github.com/manual/gh_repo_create),
[Git submodules](https://git-scm.com/docs/git-submodule).
