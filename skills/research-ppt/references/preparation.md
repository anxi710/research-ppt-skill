# Evidence preparation

## Intake

Complete this entry flow for a new research presentation. For a revision or resumed
job, restore its accepted brief first; ask only about material changes to that brief.
Repository maintenance and questions about the skill itself do not run this flow.

### Establish what is already known

Read the request, relevant prior instructions and existing workspace records. Resolve
relative entry and material paths against the request's working directory before any
`cd`; absolute paths remain valid. In a repository-root session, the entry is
`./skills/research-ppt/SKILL.md` and `<path-to-material>` denotes the supplied material
path. Check which papers, supplements, project reports, user-owned results/data/figures, reading
notes and template files are available. For a supplied folder, inventory relevant files,
identify their purpose and select explicit files; `init --source` accepts files, not
directories. Record selected source versions and fingerprints; each supplied original
is authoritative for its own recorded claims. A newer public revision does not silently
replace an uploaded version. Report unavailable/unreadable required material before
promising a workflow.

Before confirmation, file-presence checks, source identification and a small template
preview are allowed to formulate useful options. Defer substantive evidence reading,
claim selection, story design and slide production until the intake gate is satisfied.

### Resolve essential decisions interactively

Choose a short project name from the topic or source title.
Use the talk's language without claiming a research result in the filename.
For every new job, run `scripts/workflow.py init --name <project-name> ...` from the request's working directory.
If you change directories first, pass an absolute `--project` based on the original directory.
The default workspace is `./outputs/<project-name>/`.
Init preserves Chinese, cleans unsafe characters and adds `-02`, `-03` and later suffixes for duplicate names.
Without a supplied name, it uses the first source filename stem.
Explicit user names and paths override these defaults.
When resuming, reuse the original workspace.

Init creates `<private-workspace>/brief.json` and prints the actual workspace path.
Record that path.
Fill requirements from the conversation, using the [brief example](../templates/brief.example.json) for the format.
Preserve real source paths, hashes and generated design contracts.
Do not replace them with reduced, hand-authored JSON.

Without `--template`, init records `design_mode: academic_navigator` and proposes that template in `style_intent`.
It selects the actual template root in the style profile.
This proposal does not establish user approval, backend approval or completed application.
Omitting `--template` does not mean free design.
With a supplied template, init records `design_mode: user_override`.
Record the real instruction and matching style contract.

`project_name` and workspace-relative `output_files` describe the delivery defaults:
`exports/<project-name>.pptx`, `exports/<project-name>-preview.pdf` and
`exports/<project-name>-notes.md`. Use requested formats only.
Preserve explicit user filenames and old revisions.
Include the selected project path in the readable brief.
Naming defaults do not establish consent for research work.
The PDF is a preview of the final PPTX's visible slides.
When resuming, preserve saved filenames.
Preflight tests whether output paths name distinct files inside the workspace.
Custom relative filenames are allowed.
Use `--project` to set the workspace location.

Collect these decisions in `brief.json`, reusing every answer already supplied:

| Decision | What to establish |
|---|---|
| Presentation type and depth | An integrated `research_report`, a `paper_talk`, `literature_review`, `progress_report` or `method_tutorial`; depth is `overview`, `standard` or `detailed`. New initialization proposes `research_report` / `detailed`; explicit user intent wins. |
| Audience and purpose | Audience role and prior knowledge; what they should understand, discuss or decide after the talk. |
| Time | Target minutes and whether Q&A is included; when included, agree on reserved `qa_minutes`. For example, 25 minutes including 5 minutes of Q&A leaves 20 minutes for visible slides. |
| Language | Slide and delivery language, including any bilingual requirement. |
| Style and references | Desired tone/density; supplied template or reference deck and whether to follow its layout or only its visual style. Preserve or explicitly revise the proposed `design_mode` and `style_intent`; default to applying Academic Navigator. |
| Scope and structure | Main focus, required sections, exclusions and any required connection to the user's research. Record the chosen structure in `sections`. |
| Deliverables | Requested artifacts, such as editable PPTX, PDF or speaker notes. Record a nonempty `deliverables` list. |

Reuse a clearly requested report type/depth rather than asking redundant questions.
For a detailed research report, establish the central topic, must-cover questions and
exclusions in `purpose` and `sections`, including any requested connection to the user's
work. When the requested coverage cannot fit the speaking budget, propose a coherent
main deck plus detailed notes/backups; obtain agreement for material omissions or a
longer talk. Do not quietly turn a comprehensive report into a short abstract.

Initialization accepts repeated `--source` for mixed file types; actual reading depends
on available tools. Assign each source an appropriate `role` before accepting intake,
for example `research_source`, `reading_note`, `user_result`, `background_reference`
or `style_reference`. Keep the originals and hashes. A note's interpretation is not
automatically a finding of the paper it describes, and a private result is not a
published benchmark. Record a style-only reference as such rather than citing it for
research claims.

Ask about missing or contradictory essentials in small batches, normally 1–3 short
questions. Use concrete choices suited to the request and offer “you decide” when the
choice can be delegated. Do not send a questionnaire whose answers are already in
the conversation. Resolve the core audience, purpose and time rather than silently
inventing them. Propose reasonable defaults for minor unspecified details in the
summary; preserve confidentiality and other explicit constraints as well.

### Confirm the brief and record the response

Present a compact, readable summary covering the decisions above, source availability
and consequential assumptions. Distinguish user-supplied requirements, recommendations
awaiting acceptance and decisions made under an explicit delegation. Ask the user to
confirm or correct the summary, then wait. After changes, refresh the summary and seek
acceptance unless the response clearly authorizes proceeding with those changes.

An actual prior instruction to proceed with stated requirements without another
confirmation, or to let the agent choose missing details, can satisfy this gate within
its stated scope. Record the instruction and explain the resulting decisions in the
summary; do not ask again for authorization already given. A generic “make a PPT” is
not a delegation. Silence, elapsed time and a generated brief are not confirmation.
Delegation applies only to its stated scope: “you decide the style” does not resolve
an unknown audience or time budget or waive confirmation of those decisions.

Set `qa_minutes` to a positive value smaller than `target_minutes` when
`qa_time_included` is true; otherwise set it to zero. An unset Q&A inclusion decision
must be resolved before acceptance. Budget visible slides against `target_minutes`
minus `qa_minutes`.

Record `intake_confirmation` in `brief.json` with:

- `status`: `pending` until accepted, `confirmed` for an accepted brief, or `delegated`
  when an actual instruction authorizes proceeding and covers the choices made.
- `user_response`: the actual confirmation/delegation message, or a retrievable
  conversation reference. Do not invent or paraphrase approval as a user quotation.
- `requirements`: a snapshot of `audience`, `target_minutes`, `qa_time_included`,
  `qa_minutes`, `language`, `purpose`, `sections`, `style_intent`, `deliverables`, and `sources`.
  Each source entry contains only `id`, `sha256` and `role`.
  Keep assumptions separate.
  If present, include `presentation_type`, `detail_level`, `design_contract_version` and `design_mode`.
  The snapshot must match the current brief.
  Older accepted briefs without these fields remain valid.
  Do not add defaults or reopen acceptance merely because the skill changed.

From the resolved skill folder, prepare the pending requirement snapshot with
`python scripts/workflow.py intake --project <private-workspace>`. Record an accepted
status only after the real user response or qualifying prior directive.
Mandatory CLI arguments and a style profile's `verified` status do not establish
user consent. Validation can check the record and snapshot consistency, not whether
the conversation actually authorized the work; the agent must verify that evidence.

If an accepted requirement or source fingerprint changes, update the brief and obtain
confirmation for the affected material change, unless an existing delegation covers
it. Reuse unaffected accepted decisions. Pass the accepted brief and real directive
to production as constraints; still follow the current backend's own confirmation
rules and never fabricate its acknowledgments or internal design locks.

## Evidence ledger

Use `templates/evidence.example.json`. For each important claim keep:

- ID, wording and kind: source claim, author interpretation, presenter analysis, illustration.
- Source IDs and exact page/section/figure/table/equation locator.
- Conditions, limitations, numbers with units/denominators and unresolved issues.
- A review status reflecting actual reading, never optimistic auto-approval.

For cross-source synthesis, list every supporting `source_id` and qualify its locator
by source, such as `S1: Table 2; S3: results.csv, row 4, accuracy column`. Preserve
dataset, protocol, units, sample size and uncertainty differences. Separate comparable
observations, unresolved disagreements and presenter interpretations; do not average
incompatible benchmarks or present a possible explanation as an established cause.

Do not inflate a hypothesis into a proven mechanism, a nonsignificant comparison into
an established effect, or a benchmark observation into a universal limitation. Keep
original terminology; explain it rather than replacing it with a convenient synonym.
State conflicts openly. Distinguish what the authors claim from what their experiment
actually isolates, without silently replacing the author's position.

## Reading strategy

Read the problem and contributions, then task/formalization, method, metric definitions,
main evidence and limitations. Read appendices supporting selected claims and examples.
Select figures only after interpreting their axes, legend, experimental scope and caption.
For raw-result data supplied by the user, retain file/column/row locators and processing steps.

Read mixed materials according to their role: project reports for objectives and progress,
logs/data for observed results and conditions, notes for leads and interpretation, papers
for cited methods and published evidence. Reconcile terminology across sources without
erasing real differences. If a cited original is absent, identify the claim as supported
only by the supplied secondary material; flag the gap rather than inventing an original
locator or fetching unrelated literature to fill the deck. For necessary background or
benchmark concepts, purposeful primary-source image sourcing is allowed unless the
user restricts sources or browsing. Record the external image as attributed context,
not new result evidence, following `story-and-style.md`. Adding substantive research
claims still requires the accepted scope or an authorized source-gap resolution.

Prioritize text extraction and native page rendering. OCR is a last resort for genuinely
image-only content; manually confirm numerals, signs, subscripts and axis text. An image
of a table can override a parser that lost columns; record the discrepancy.

## Exit review

Can a reviewer trace each main takeaway to concrete evidence? Are prerequisites defined?
Are source-derived observations, outside background, author conjectures and our analysis
separated? Do source gaps or contradictions materially change the talk? Do not advance
while a key figure or important result is merely guessed.
