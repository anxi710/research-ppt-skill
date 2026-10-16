# Research PPT Skill

<p align="center">
  <a href="CHANGELOG.md"><img src="https://img.shields.io/static/v1?label=Skill&amp;message=v0.4.1&amp;color=2563eb" alt="Skill v0.4.1" height="20"></a>
  <a href="skills/research-ppt/references/environment-setup.md"><img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&amp;logoColor=white" alt="Python 3.11" height="20"></a>
  <a href="https://github.com/anxi710/research-ppt-skill/actions/workflows/ci.yml"><img src="https://github.com/anxi710/research-ppt-skill/actions/workflows/ci.yml/badge.svg?branch=main" alt="Validate skill" height="20"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT" height="20"></a>
</p>

[简体中文](README.zh-CN.md) · [Skill entry](skills/research-ppt/SKILL.md) · [Architecture](docs/architecture.md)

**Understand the evidence. Design the talk. Delegate production. Review the actual deck.**

A reusable agent skill for detailed research-report presentations built from supplied papers, reading notes, experimental results, data, figures and reports. The agent organizes them around a research topic or question, distinguishing published claims, your own results and presenter analysis. Single-paper talks, journal clubs, literature reviews, progress reports and method tutorials are also supported. It works with an agent that can read files, execute code and view images; it is not a hosted service.

## Responsibility boundary

| Research PPT Skill owns | ppt-master owns |
|---|---|
| Source/version checks and evidence extraction | Production routing and its own runtime |
| Audience prerequisites, argument and time budget | SVG/native-slide authoring and layout |
| Style decisions and original-figure preparation | PPTX export, notes, animations if requested |
| Page-level production brief | Its own native technical checks |
| Independent factual, visual and artifact review | Requested local repairs and re-export |

The `ppt-master` submodule tracks upstream `main`. Before each new production job, check for updates and read the current instructions. Record the actual revision used, and do not silently upgrade midway through a job. **Git submodules necessarily record a commit; tracking the latest version is an update policy, not the absence of a commit ID.**

## Usage

### First-time use

The examples below run from the checkout root after `cd research-ppt-skill`.
Replace `<path-to-material>` with your material folder's absolute or relative path;
relative paths resolve from the request's working directory. Absolute skill paths
also work when you run elsewhere.

1. **Obtain the skill and backend** so the agent can read their local instructions:

   ```bash
   git clone --recurse-submodules <repository-url> research-ppt-skill
   cd research-ppt-skill
   ```

2. **Ask the agent to configure and check the environment.** The
   [environment setup guide](skills/research-ppt/references/environment-setup.md)
   covers Python, helper/backend dependencies, a real PPTX renderer and checks:

   > Read `./skills/research-ppt/references/environment-setup.md`, configure this
   > project's environment, and report the dependency, backend and real PPTX-rendering
   > check results.

   To reuse an environment, add "Use my existing conda docs environment."
   `docs` is an optional example name; choose your own environment as needed.

3. **Describe the talk and confirm the brief.** Give an agent that can read files,
   run code and inspect images the skill path, sources, audience, time,
   language, style and outputs:

   > Read `./skills/research-ppt/SKILL.md` and make a detailed research-report PPT
   > from `<path-to-material>`, including its papers, notes and my experiment results.
   > Organize it around our research question for graduate students with a basic
   > understanding of machine learning. Use Chinese and a clean academic style; allow
   > 25 minutes including 5 minutes of Q&A. Distinguish published findings, my results
   > and analysis; flag missing evidence. Deliver PPTX, PDF and detailed speaker notes.
   > Summarize the requirements for my confirmation first.

   You can supply a folder of materials. The agent selects relevant files and builds
   one coherent report; detailed notes and hidden backups support a main deck fitted
   to the agreed time. Missing evidence is flagged. Explicit single-paper and other
   focused requests keep their scope.

4. **Find the talk under `./outputs/`.** The agent summarizes a short project name from
   your topic or source title and creates `./outputs/<project-name>/` under the
   request's working directory. Requested exports default to
   `<project-name>.pptx`, `<project-name>-preview.pdf` and
   `<project-name>-notes.md` in its `exports/` folder. Your explicit names and
   directory take priority. See the [brief example](skills/research-ppt/templates/brief.example.json). After your
   confirmation or explicit scoped delegation, the agent prepares the evidence,
   delegates production to ppt-master, then renders and reviews every final PPTX slide.
   See the [full seven-step guide](docs/usage.md#first-time-use) for purposes and completion criteria.

Without a different requested style, new talks use the built-in Academic Navigator
template: an information cover, separated main-section tabs, title rules, current-page
badges and consistent content components. Hidden backups stay out of navigation.
The agent selects and installs the template, checks the actual renders and repairs
readability defects before delivery.
See [production handoff](skills/research-ppt/references/production-handoff.md).

Optional concept illustrations: see the [Codex, Claude Code and API image generation guide](skills/research-ppt/references/image-generation.md) (Chinese setup steps).

### Ongoing use and maintenance

Use a new workspace for each new talk; resume an existing talk from its saved records.
Update the skill/backend between jobs and validate reusable changes. Follow the
[maintenance scenarios](docs/usage.md#ongoing-use-and-maintenance) for the relevant steps.

## Workflow and files

```text
Confirm brief → evidence → audience/story → style/assets → production handoff
                                                      ↓
                                              current ppt-master
                                                      ↓
                 delivery ← gate ← inspect final PPTX ← export
                                      ↓ defects
                               revision request → repair → rerender
```

The private workspace keeps `brief.json` beside `inputs/`, `analysis/`, `assets/`,
`design/`, `notes/`, `handoff/`, `production/`, `qa/`, and `exports/`. Repository-local
`outputs/` is ignored; keep these private job artifacts out of commits and publication.

Sources, evidence, figure inventory, style profile and slide plan become an
immutable, checksummed production handoff. The tools validate metadata and artifact
consistency; the agent must still read the sources, choose crops, judge claims,
inspect rendered slides, and perform repairs. [Runbook](docs/runbook.md).

## Scope and licensing

This repository contains generic instructions, helper code, schemas/examples and
synthetic test inputs only. No user papers, institutional logos, private slides,
font binaries, model credentials, or accepted private case are included.

Original code and documentation: **MIT**, matching ppt-master's current root license.
Third-party materials/dependencies keep their own licenses. See
[LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Skill versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
Use [bump_version.py](scripts/bump_version.py) to prepare a version; see the
[changelog](CHANGELOG.md) and [versioning instructions](CONTRIBUTING.md#versioning).

## Validation status

The included helpers are locally testable without network calls or model usage.
Backend generation and remote Dependabot/Actions execution
must be tested in an authenticated, network-enabled environment; offline unit tests
are not evidence that those remote operations succeeded.
