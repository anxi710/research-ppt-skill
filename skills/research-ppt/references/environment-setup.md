# Agent environment setup

Use this file when the user asks an agent to configure Research PPT Skill. Complete
setup and report the results; this request does not start presentation intake,
research reading, production or publication. Use synthetic fixtures for verification.

## 1. Resolve the installation and user choices

**Purpose:** establish the actual paths and environment before changing anything.

- Resolve the absolute skill directory containing `SKILL.md`, `references/` and
  `scripts/`; read that `SKILL.md`. In a repository checkout, also read the applicable
  `AGENTS.md` and resolve the repository root. A separately installed skill need not
  have the repository's maintenance scripts, requirements file or tests.
- Accept the repository-root entry `./skills/research-ppt/references/environment-setup.md`.
  Resolve relative user paths against the request's working directory before any `cd`;
  the user need not rewrite them as absolute paths. Internal script/reference paths
  use the resolved installation directory. Absolute paths remain supported.
- Reuse the user's selected Python/conda environment. An environment name such as
  `docs` is a user choice, not a built-in default. Otherwise create an isolated
  environment in an appropriate writable location. Do not change unrelated global
  packages, shell startup files or the user's default environment.
- Resolve the backend from this checkout's configured Git submodule or the user's
  supplied ppt-master checkout path. Resolve a relative path against the request's
  working directory and record the real absolute location. Do not guess another
  installation.
- Record the request's working directory before changing directories. Presentation
  jobs default to its `./outputs/<project-name>/`, with delivery files
  `<project-name>.pptx`, `<project-name>-preview.pdf` and `<project-name>-notes.md`
  in that workspace's `exports/`. Honor explicit destination/name choices and saved
  paths for resumed jobs. Check that the output parent is writable; setup does not
  create a real talk or `brief.json`.

## 2. Inspect and install helper dependencies

**Purpose:** make the preparation and review tools work in the selected environment.

Record `sys.executable`, Python version, platform and package import results. Python
3.11 is required. In commands below, `python` means that selected interpreter with
its environment active; use `conda run -n <chosen-name>` where appropriate. Use its
`python -m pip`, never a potentially unrelated `pip` executable.

In repository mode, inspect and install from the current root `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

For a separately installed skill, inspect the actual helper imports and install the
needed helper dependencies: `python-pptx>=1.0`, `Pillow>=10`, `lxml>=4.9` and
`pypdfium2>=4.30`. Check imports `pptx`, `PIL`, `lxml` and `pypdfium2` using the
selected interpreter. These are helper dependencies; they do not install ppt-master.
Install only missing/incompatible packages and requirements needed for setup.

## 3. Inspect and configure the current backend

**Purpose:** prepare the real production backend without fixing its interface here.

In repository mode, run `python scripts/upstream.py status` from the resolved root
to inspect the configured submodule. Before new work, use its documented `update`
action when network access and the user's scope permit. Do not update during active
production/review, discard dirty files or override an unrecorded backend revision;
report these conditions. A status probe does not establish remote freshness.

For a supplied separate checkout, inspect its real path, revision, dirty state and
configured remote. Update its intended branch only when the same conditions hold;
do not assume repository maintenance helpers exist in a standalone installation.

Read the resolved backend's current `AGENTS.md`, skill entry and installation
instructions before executing backend setup. Follow its current required entry and
integrity gates; stop backend execution if a gate fails. Discover setup commands,
dependency files and optional environment checks from those instructions. Do not
hard-code a remembered backend CLI or bypass a gate. Do not edit backend source to
make checks pass.
Record the revision, documents read and license observation, including whether MIT
is observed. Backend documentation does not authorize publishing data or changing
research claims. Do not start a production route merely to test installation.

## 4. Enable real PPTX rendering

**Purpose:** verify exported PPTX files rather than relying on source previews.

The bundled `scripts/decktools.py render-pptx` needs LibreOffice (`soffice` or
`libreoffice`) and `pypdfium2`. Detect the actual executable and version. Install
platform-appropriate rendering support when permitted, or report the exact blocker.
For the default style, verify that Times New Roman and Microsoft YaHei are both
installed and visible to the backend and the PPTX renderer. Report an unavailable
face rather than silently replacing it; an explicit user font choice overrides the
default. Use installed fonts; do not copy font files into the repository. A successful import
or an SVG preview alone does not establish that PPTX rendering works.

## 5. Verify using the available installation

**Purpose:** distinguish tested readiness from an installation that is only partial.

Read the installed helper's `--help` before using its current subcommands. Perform
only documented backend environment checks that need no credentials, paid services
or presentation content. Do not request secrets. Honor tool/sandbox permissions;
continue within the setup authorization already given and report real blockers.

**Repository checkout:** run the required suite once from its root. If LibreOffice
is available on the test process's PATH, enable the real render test on that run:

```bash
RUN_RENDER_TESTS=1 python -m unittest discover -s tests -v
python scripts/check_repo.py
```

Set the environment variable using the platform's syntax. Without a renderer, run
the suite without `RUN_RENDER_TESTS=1` and report rendering as skipped/blocked.
The render test checks all slides, visible slides and unchanged input bytes. Rerun
only after a repair or when a failure needs diagnosis; never weaken tests to pass.

**Separately installed skill:** repository tests are unavailable. In a temporary
private directory, create a two-slide synthetic PPTX with `python-pptx`: one visible
slide, one hidden backup (`slide._element.set('show', '0')`), native text and nonempty
speaker notes on both (`slide.notes_slide.notes_text_frame.text = 'Synthetic note'`).
Save it and record its SHA-256. Consult the current helper help, then run:

```bash
python <skill-dir>/scripts/decktools.py audit --pptx <fixture.pptx> --out <audit.json>
python <skill-dir>/scripts/decktools.py render-pptx --pptx <fixture.pptx> --out <all-dir> --include-hidden
python <skill-dir>/scripts/decktools.py render-pptx --pptx <fixture.pptx> --out <visible-dir>
```

Replace placeholders with quoted resolved paths. Relative paths work from the recorded
working directory; absolute paths are useful after directory changes. Require audit
pass, two all-slide pages with mapping `[1, 2]`, one visible page with mapping `[1]`, readable rendered
images and an unchanged original hash. If any check cannot run, report that limit.

## 6. Report setup status

**Purpose:** give the user a reproducible account of what works and what remains.

Report the selected interpreter/environment, helper package checks, resolved backend
path/revision, instructions read, freshness and license observation, renderer/version,
tests/checks passed, skipped or failed, and concrete blockers. State partial readiness
when rendering or a required backend check is unavailable. Setup checks do not certify
production or replace independent review of an actual final deck.

Optionally save a local record to ignored `local/environment.local.json` in repository
mode, or a private external path in standalone mode. Exclude credentials, fonts and
user research materials; do not commit or publish environment artifacts.
