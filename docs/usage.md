# Usage guide

[简体中文](usage.zh-CN.md) · [README](../README.md) · [Agent runbook](runbook.md)

This guide covers the user lifecycle: first-time setup, making a talk, resuming
work and maintaining the installation. Each step explains its purpose, who acts
and when it is complete. The [runbook](runbook.md) provides detailed agent commands
and record formats for preparation, production and review.

## First-time use

Follow these steps for the first talk using Python 3.11. The examples below run
from the checkout root after `cd research-ppt-skill`. Replace `<path-to-material>`
with the actual material folder; it may be an absolute or relative path.

Before changing directories, the agent records the absolute working directory of
the user's request and resolves relative skill-entry and material paths against
it. That directory is the default output root, even when the skill is installed
elsewhere. The agent locates the actual skill and scripts and uses their resolved
absolute paths internally. Absolute entry and material paths remain valid when
running elsewhere. Run `init` in the request directory with the resolved script
path, or pass the captured absolute workspace path with `--project` after changing
directories; also use resolved material paths. These examples use the checkout
root as the request directory, so their private `./outputs/` is ignored by Git.

The user provides sources and requirements; the agent normally maintains the private
workspace and JSON records. The default proposal is a detailed research report that
integrates the supplied papers, reading notes, experimental results, data, figures
and reports around a topic or question. Explicit single-paper talks remain supported.
The agent reads and synthesizes; the helpers organize and validate records, while
ppt-master performs slide production.

### Step 1. Obtain the repository and install helper dependencies

**Purpose:** Make the complete parent skill, its preparation tools and backend
checkout available locally.

**Action (user or agent):** Clone the repository with its submodule and install the
parent helper dependencies in your chosen Python environment:

```bash
git clone --recurse-submodules <repository-url> research-ppt-skill
cd research-ppt-skill
python -m pip install -r requirements.txt
```

For agent-run setup, clone first and ask the agent to follow the
[environment setup guide](../skills/research-ppt/references/environment-setup.md)
for this step and step 2. Name your preferred Python environment, for example:
"Use my existing conda docs environment." `docs` is an optional example, not a
repository requirement; the agent should report the interpreter actually selected.

**Done when:** `skills/research-ppt/` and `third_party/ppt-master/` are available,
a Python 3.11 interpreter is selected and helper dependency installation succeeds.
Backend installation is a separate step below.

### Step 2. Prepare the backend and rendering environment

**Purpose:** Establish which production instructions and actual backend revision
will be used, and make final-PPTX inspection possible.

**Action (user or agent):** Before beginning a production job, check the configured
backend branch and record its local state:

```bash
python scripts/upstream.py update --out outputs/backend-observation.local.json
python scripts/upstream.py status
```

`update` fetches the configured upstream branch when network access permits;
`status` only reports the local checkout and does not check remote freshness. If
updating fails, retain the actual revision and report that freshness was not
verified. If local changes or an unrecorded backend revision block the update,
resolve them as described in maintenance step 3 below.

The agent must open the current `AGENTS.md` and skill entry in the real backend
path reported by the helper, then install its dependencies and follow its current
runtime instructions. The parent `requirements.txt` does not install that runtime.
Also arrange a real PPTX renderer: the bundled `render-pptx` helper uses
LibreOffice/soffice. Another renderer must provide equivalent, truthful all-slide
render records. Reading a status report alone does not complete this setup.

If delegating these tasks, the same
[environment setup guide](../skills/research-ppt/references/environment-setup.md)
also covers backend discovery and rendering. Run its helper and real-render checks
and report actual passes, skips and blockers.

**Done when:** The chosen Python and helper dependencies are recorded, current
backend instructions have been read and the actual revision recorded, and the
backend environment and real PPTX renderer have been checked. Keep that revision
stable throughout production and review for this talk. Report any incomplete
checks rather than treating partial setup as ready.

### Step 3. Describe the talk to the agent

**Purpose:** Give the agent the source material and communication goal so it can
ask only for missing information.

**Action (user):** Use an agent that can read files, execute code and inspect images.
Give it the skill entry path, such as `./skills/research-ppt/SKILL.md`, the material paths
(files or a folder), research topic/question, audience and prior knowledge, purpose,
duration and Q&A allocation, language, style/reference, focus and deliverables.
For example:

> Read `./skills/research-ppt/SKILL.md` and prepare a detailed research-report PPT
> from `<path-to-material>`. Inventory its papers,
> reading notes and my experimental results, then organize them around the project
> research question. The audience is AI researchers who understand basic machine
> learning but are new to this subfield. Cover the necessary background, problem,
> mechanism/methods, evidence, comparisons, limitations and my progress/next steps
> where supported. Distinguish published claims, my results and analysis; flag gaps.
> The total slot is 25 minutes, including 5 minutes of Q&A. Use Chinese with original
> English technical terms, a clean academic style and original figures. Keep main
> slides concise, with detailed notes and hidden backups. Deliver PPTX, PDF and notes.
> Summarize the requirements for my confirmation before preparing the evidence.

New briefs propose `presentation_type: research_report` and `detail_level: detailed`.
You can instead request a single-paper talk, literature review, progress report or
method tutorial, with standard or overview depth. The other choices above are examples.
The skill does not assume an institution, discipline, color, language, slide count
or presenter.
[`academic-blue.json`](../skills/research-ppt/profiles/academic-blue.json) is an
optional neutral blue-and-white style without institutional branding.

For automatic discovery, optionally copy or symlink the **complete**
`skills/research-ppt/` folder into your host's skill location. Its references,
scripts and templates are required; copying only `SKILL.md` is insufficient.
Supply the backend path explicitly if installed separately.

The agent uses the supplied materials and flags missing evidence rather than
inventing results or automatically expanding the research. Folder inventory and
source selection are agent work, not automatic interpretation by the helper.

**Done when:** The agent has read the parent skill, located the supplied sources
and reused requirements already given. It asks short batches of questions only
about missing or contradictory essentials; acceptance happens in step 5.

### Step 4. Create a private workspace and locate `brief.json`

**Purpose:** Keep this talk's inputs, requirements and later outputs together,
with source fingerprints that identify the material actually used.

**Action (normally the agent):** Summarize a short, descriptive project name from
the supplied topic or source title, then initialize a new private workspace. Naming
does not require substantive evidence reading; avoid adding unsupported research
claims. Use a safe single path component, preserving Chinese when present. Replace
the quoted material placeholders below with real paths before running:

```bash
python ./skills/research-ppt/scripts/workflow.py init \
  --name synthetic-research-report \
  --source "<path-to-material>/paper-a.pdf" \
  --source "<path-to-material>/paper-b.pdf" \
  --source "<path-to-material>/reading-notes.md" \
  --source "<path-to-material>/experiment-results.csv" \
  --presentation-type research_report --detail-level detailed \
  --minutes 25 --language zh-CN \
  --audience "AI researchers familiar with basic ML but new to this subfield"
```

Without `--project`, `init` creates `./outputs/<safe-project-name>/` relative to its
working directory and prints the actual path. This example, run from
`/workspace/research-ppt-skill`, creates
`/workspace/research-ppt-skill/outputs/synthetic-research-report/brief.json`. Use that
printed path in later commands; substitute it for the example paths below. If the
same name already exists, a new project receives `-02`, `-03`, and so on; it does
not overwrite or implicitly resume a talk. Explicit `--project` takes priority and
must identify a new, empty workspace. Relative overrides resolve from the command's
working directory. An explicitly supplied directory or filename always wins.

The agent supplies `--name`; if omitted, the helper only falls back to the source
filename stem and does not summarize meaning. For a supplied folder, the agent
inventories it, identifies readable relevant materials and repeats `--source` for
each selected file; `init --source` accepts files, not directories. It copies and
fingerprints files, but does not read or synthesize their contents. Optionally add
`--template /path/to/reference.pptx` for style guidance.

Initialization calculates SHA-256 hashes and initially labels regular inputs
`research_source` (the template is `style_reference`). The agent then sets each
source's appropriate metadata role: `research_source`, `reading_note`, `user_result`,
`background_reference` or `style_reference`, retaining generated IDs, paths and
hashes. Keep the actual inventory rather than replacing it with example records.
Source roles are part of the requirements accepted in step 5.

Keep working artifacts in this workspace. Requested accepted exports default to
`exports/synthetic-research-report.pptx`, `exports/synthetic-research-report-preview.pdf` and
`exports/synthetic-research-report-notes.md`; create only the requested formats. The
optional `project_name` and `output_files` brief fields record naming defaults and
explicit overrides, not requirement acceptance. These private files must not be
committed or published, including when stored in the repository's ignored `outputs/`.

For a paper-free demonstration, optionally run
`python examples/synthetic/prepare.py --out outputs/synthetic-research-report-demo`, then open
`outputs/synthetic-research-report-demo/brief.json`. This synthetic preparation fixture uses fictional
acceptance for testing; it supplies neither real user consent nor a produced PPT.
Do not reinitialize an existing accepted workspace to resume a talk.

**Done when:** The private workspace contains `brief.json` and copied inputs with
their fingerprints. Intake remains pending; initialization alone does not authorize
preparation or produce a deck.

### Step 5. Complete and confirm the brief

**Purpose:** Agree on the communication requirements before evidence preparation
and narrative design, including how much time the slides actually have.

**Action (agent, then user):** The agent fills the brief from the conversation,
records each source's exact version, and proposes any unspecified choices. See the
complete [synthetic `brief.json` example](../skills/research-ppt/templates/brief.example.json).
Selected fields for the example request are:

```json
{
  "presentation_type": "research_report",
  "detail_level": "detailed",
  "audience": "AI researchers familiar with basic ML but new to this subfield",
  "target_minutes": 25,
  "qa_time_included": true,
  "qa_minutes": 5,
  "language": "zh-CN",
  "purpose": "Explain the research question, methods, evidence, synthesis and our progress",
  "sections": ["Background", "Problem", "Methods", "Evidence", "Synthesis", "Limitations", "Progress and next steps"],
  "style_intent": "Clean academic style, original figures, concise text, no institutional branding",
  "deliverables": ["pptx", "pdf", "speaker_notes"]
}
```

Here the 25-minute slot includes 5 minutes of Q&A, leaving **20 minutes of speaking
time**. `init` leaves the Q&A policy unspecified and style intent empty; other
initial values, including report type and depth, are proposals until accepted.
The agent may edit `presentation_type` and `detail_level` in the brief before intake;
when present, both are captured in the acceptance snapshot. Legacy briefs without
these fields remain valid and must not be silently rewritten. After completing
these choices, the agent creates the requirement snapshot:

```bash
python ./skills/research-ppt/scripts/workflow.py intake --project outputs/synthetic-research-report
```

The command writes a **pending** snapshot in `brief.json.intake_confirmation`.
The agent presents a readable summary distinguishing supplied requirements,
proposed defaults and delegated decisions. You accept or correct it. You may also
explicitly delegate choices, for example: "Start with these requirements; choose
the palette and slide count for me."

Only an actual user reply or a prior explicit instruction authorizing the stated
brief or relevant delegated choices justifies recording `confirmed` or
`delegated`, with the real quote or a retrievable reference in `user_response`.
A generic request to make a PPT is not delegation. Scripts do not supply consent;
preparation checks reject pending or stale confirmation. Changed key requirements
need renewed confirmation, and parent confirmation does not replace backend gates.

**Done when:** The brief captures the accepted requirements, Q&A reservation and
source identities, and its confirmation record matches a real user instruction.
The agent can now begin substantive preparation.

### Step 6. Prepare evidence, story and assets; create the handoff

**Purpose:** Turn the accepted brief and original sources into a traceable
production plan that preserves the research claims and figure context.

**Action (agent):** Read the sources, record evidence and figure provenance,
inspect original figures, design the story and timing, and complete the style
profile and slide plan. Organize by the research question rather than by file order;
trace each claim to its source and distinguish published findings, user results and
presenter analysis. A reading note helps navigation but does not prove a published
claim when its original source is missing. Mark evidence gaps and unresolved conflicts.

Detailed coverage explains necessary background, the problem, mechanisms/methods,
evidence, comparisons/synthesis and limitations; include the user's progress and
next steps only where supported by supplied materials. Main slides fit the agreed
speaking time, with supporting details in useful notes and genuinely hidden backup
slides. There is no fixed page count and detail does not mean dense slide text.
When those records and assets are ready, run:

```bash
python ./skills/research-ppt/scripts/workflow.py preflight \
  --project outputs/synthetic-research-report --out outputs/synthetic-research-report/qa/preflight.json
python ./skills/research-ppt/scripts/workflow.py handoff \
  --project outputs/synthetic-research-report --run-id run-01
```

An initialized workspace alone will fail preflight; the agent must complete and
inspect the preparation first. The handoff is an immutable snapshot, not an upload.
Give `outputs/synthetic-research-report/handoff/run-01/handoff.md` to the agent executing
ppt-master. See the [runbook](runbook.md) for detailed preparation commands.

**Done when:** Preflight passes, the agent has checked the evidence and assets,
and the handoff contains the agreed slide requirements, notes and acceptance
criteria with source and asset references.

### Step 7. Produce, review and deliver the actual deck

**Purpose:** Verify that the exported presentation communicates the accepted
research accurately and remains readable in its final PPTX form.

**Action (agent):** Follow the current ppt-master route and its required gates to
produce the deck and a truthful build receipt. Audit and render the **actual final
PPTX**, including hidden backup slides, then inspect every slide and necessary
figure crops against the preparation contract. Backend checks and SVG previews do
not replace this review. Repair defects and create fresh render/review records
for changed artifacts; preparation changes also require a new handoff.

Run the final acceptance gate with records bound to the final PPTX. The delivered
`-preview.pdf` is an actual rendering of the visible slides. Independently render
and review all slides, including hidden backups. Deliver the
requested PPTX, PDF, speaker notes and provenance files from the private workspace,
with existing paths and any remaining limitations. The [runbook](runbook.md)
details rendering, review and gate commands. Without actual PPTX rendering, label
the result as an unvalidated draft.

**Done when:** The final gate passes, the independent review covers every final
slide, and the agreed deliverables are available with matching records.

## Ongoing use and maintenance

Choose the scenario that applies; these are not four steps to repeat for every talk.

### Step 1. Start another talk

**Purpose:** Reuse the installation while keeping different talks' sources,
requirements and results separate.

**Action (user and agent):** Reuse the installed dependencies and check/update the
backend **between jobs**, following first-time step 2 and maintenance step 3 as
needed. Summarize the new project name and repeat first-time steps 3–7 with the new
sources and requirements. `init` creates a fresh workspace under the request's
`outputs/`; same-name projects receive a numeric suffix. Use the path it prints.

**Done when:** The new talk has its own brief, source inventory, confirmed
requirements and production/review records. Earlier accepted talks remain intact.

### Step 2. Resume or revise an existing talk

**Purpose:** Continue from durable records while ensuring any new output is
reviewed against the requirements and sources that actually produced it.

**Action (agent):** Use the explicitly identified original workspace and reopen its
brief, sources, preparation, handoffs and QA records; do not run `init` again. Reuse the accepted brief and
confirm material changes to requirements or source identities/content/roles.
Preserve existing workspace and `output_files` paths; new naming defaults alone
are not a reason to rewrite them.
Keep the recorded backend revision during the active job. If evidence, assets or
the slide plan change, create a new handoff with a new run ID; for production-only
repairs, reuse the applicable handoff. Produce the revised artifact, then audit,
render, review and gate it with fresh records. Preserve earlier accepted versions,
handoffs and review records rather than overwriting them.

**Done when:** The revised artifact passes review against its applicable handoff,
and old approvals have not been reused for a changed file.

### Step 3. Update the skill or backend

**Purpose:** Receive improvements without losing local work or changing the
production environment midway through a talk.

**Action (user or maintainer):** Update between active jobs. Inspect and save local
edits first; run the parent pull only with a clean parent checkout:

```bash
git status --short
git pull --ff-only
git submodule update --init --recursive
```

The submodule command restores the backend revision recorded by the parent
checkout; it does **not** select the latest upstream `main`. To fetch the
configured upstream branch deliberately, use:

```bash
python scripts/upstream.py update --out outputs/backend-observation.local.json
python scripts/upstream.py status
```

The helper refuses dirty backend files or a backend revision not yet recorded in
the parent gitlink; review and resolve those states instead of discarding changes.
After a backend change, reread its current entry instructions, adjust dependencies
as needed and validate representative slides before adopting it for production.
Maintainers review and record the updated gitlink. Dependabot proposes submodule
updates on workdays; those proposals require maintainer review and do not merge
silently. See the [upstream policy](upstream.md).

**Done when:** Local changes are preserved, the actual backend revision and its
current instructions are known, and representative production has been validated.
The helper's file/license observations alone do not certify backend compatibility.

### Step 4. Validate reusable skill changes

**Purpose:** Check that shared instructions and helpers still work without
placing private research artifacts in the repository.

**Action (contributor):** For changes to the reusable skill or repository, run:

```bash
python -m unittest discover -s tests -v
python scripts/check_repo.py
```

With LibreOffice available, optionally include the synthetic rendering integration
test with `RUN_RENDER_TESTS=1 python -m unittest discover -s tests -v`. This checks
the local rendering helper, not ppt-master production compatibility. Report
content/layout failures using the issue templates and use minimal synthetic
regression fixtures for shared-rule changes. Keep user workspaces, raw papers,
private decks, credentials and font files out of commits. See
[Contributing](../CONTRIBUTING.md).

**Done when:** Required checks pass, any new regression fixture is synthetic, and
shared changes contain no private materials. Backend changes additionally need
the representative production validation described in maintenance step 3.
