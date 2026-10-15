# Evidence preparation

## Intake

Complete this entry flow for a new research presentation. For a revision or resumed
job, restore its accepted brief first; ask only about material changes to that brief.
Repository maintenance and questions about the skill itself do not run this flow.

### Establish what is already known

Read the request, relevant prior instructions and existing workspace records. Check
which papers, supplements, user-owned results, reading notes and template files are
available. Record source versions and fingerprints; source PDFs remain the authority
for the specified version. A newer public revision does not silently replace an
uploaded version. Report unavailable required material before promising a workflow.

Before confirmation, file-presence checks, source identification and a small template
preview are allowed to formulate useful options. Defer substantive evidence reading,
claim selection, story design and slide production until the intake gate is satisfied.

### Resolve essential decisions interactively

Collect these decisions in `brief.json`, reusing every answer already supplied:

| Decision | What to establish |
|---|---|
| Audience and purpose | Audience role and prior knowledge; what they should understand, discuss or decide after the talk. |
| Time | Target minutes and whether Q&A is included; when included, agree on reserved `qa_minutes`. For example, 25 minutes including 5 minutes of Q&A leaves 20 minutes for visible slides. |
| Language | Slide and delivery language, including any bilingual requirement. |
| Style and references | Desired tone/density; supplied template or reference deck and whether to follow its layout or only its visual style. Record the agreed intent as `style_intent`. |
| Scope and structure | Main focus, required sections, exclusions and any required connection to the user's research. Record the chosen structure in `sections`. |
| Deliverables | Requested artifacts, such as editable PPTX, PDF or speaker notes. Record a nonempty `deliverables` list. |

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
  Each source entry contains only `id`, `sha256` and `role`; assumptions are kept
  separately. The snapshot must match the current brief.

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

Prioritize text extraction and native page rendering. OCR is a last resort for genuinely
image-only content; manually confirm numerals, signs, subscripts and axis text. An image
of a table can override a parser that lost columns; record the discrepancy.

## Exit review

Can a reviewer trace each main takeaway to concrete evidence? Are prerequisites defined?
Are source-derived observations, outside background, author conjectures and our analysis
separated? Do source gaps or contradictions materially change the talk? Do not advance
while a key figure or important result is merely guessed.
