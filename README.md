# Research PPT Skill

[简体中文](README.zh-CN.md) · [Skill entry](skills/research-ppt/SKILL.md) · [Architecture](docs/architecture.md)

**Understand the evidence. Design the talk. Delegate production. Review the actual deck.**

A reusable agent skill for paper presentations, journal clubs, research progress
reports, method tutorials, and literature reviews. It works with a tool-capable
agent; it is not a hosted service or a one-command autonomous paper-reading model.

## Responsibility boundary

| Research PPT Skill owns | ppt-master owns |
|---|---|
| Source/version checks and evidence extraction | Production routing and its own runtime |
| Audience prerequisites, argument and time budget | SVG/native-slide authoring and layout |
| Style decisions and original-figure preparation | PPTX export, notes, animations if requested |
| Page-level production brief | Its own native technical checks |
| Independent factual, visual and artifact review | Requested local repairs and re-export |

We do not freeze, vendor, or reimplement a historic ppt-master exporter. The backend
is a submodule tracking upstream `main`; new production jobs update it, inspect
its current instructions, and record the actual revision used. Git necessarily
records a commit in each repository snapshot—this is provenance, **not a permanent
compatibility pin**. No silent upgrade occurs midway through an accepted job.

## Setup

After publication, clone this repository with `--recurse-submodules`.
The downloadable pre-publication package also supports `python scripts/restore_git.py`.

```bash
python -m pip install -r requirements.txt
python scripts/upstream.py update
python scripts/upstream.py status
python -m unittest discover -s tests -v
```

Backend installation and generation follow the checked-out ppt-master's own
instructions. This skill does not assume a stable `generate` command.

Give your agent the absolute path to `skills/research-ppt/SKILL.md`, the source
papers, an optional style reference, your audience, talk duration and output language.
The parent skill first resolves missing requirements and presents a brief covering
purpose, audience, time/Q&A, language, style, structure and deliverables. It waits for
acceptance before evidence preparation; you may explicitly delegate choices or authorize
the supplied requirements without another round. Existing answers are reused.
Copy/symlink the complete `research-ppt` skill folder into your host's skill discovery
location when desired; supply the backend path explicitly if installed separately.
Do not copy only SKILL.md: the references, scripts and templates are part of the skill.

Example request:

> Use Research PPT Skill to make a 27-minute paper presentation for AI researchers
> outside this subfield. Follow background, problem, method, experiments, conclusions
> and analysis. Use original paper figures; keep slide text short and put detailed
> reading guidance in speaker notes. Prepare evidence and a style brief first,
> delegate production to the current ppt-master, then render, inspect and repair
> every slide including hidden backup slides before delivery.

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

Initialize a **private** workspace outside this repository:

```bash
python skills/research-ppt/scripts/workflow.py init \
  --project ../my-research-talk --source /path/paper.pdf \
  --minutes 27 --language zh-CN --audience "AI researchers outside this subfield"
```

Fill the remaining brief fields, then run
`python skills/research-ppt/scripts/workflow.py intake --project ../my-research-talk`
to create a pending requirement snapshot, not consent.
Record only the user's actual acceptance or delegation in
`brief.json`. Preparation checks and handoff reject pending or stale confirmation.

Sources, evidence, figure inventory, style profile and slide plan become an
immutable, checksummed production handoff. The tools validate metadata and artifact
consistency; the agent must still read the sources, choose crops, judge claims,
inspect rendered slides, and perform repairs. [Runbook](docs/runbook.md).

## Updates and iteration

`python scripts/upstream.py update` advances to upstream `main` without discarding
local changes. Dependabot is configured to propose submodule updates on workdays;
maintainers review those PRs. It does not silently merge upstream code. An upstream
update requires rereading backend instructions and representative-slide validation.
The local helper records the revision and license/entry-file observations, but does
not certify complete backend compatibility. [Upstream policy](docs/upstream.md).

Submit content/layout failure reports using the issue templates. Add a minimal,
synthetic regression fixture before changing shared rules. [Contributing](CONTRIBUTING.md).

## Scope and licensing

This repository contains generic instructions, helper code, schemas/examples and
synthetic test inputs only. No user papers, institutional logos, private slides,
font binaries, model credentials, or accepted private case are included.

Original code and documentation: **MIT**, matching ppt-master's current root license.
Third-party materials/dependencies keep their own licenses. See
[LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Validation status

The included helpers are locally testable without network calls or model usage.
Backend generation, GitHub publication, and remote Dependabot/Actions execution
must be tested in an authenticated, network-enabled environment; offline unit tests
are not evidence that those remote operations succeeded.
