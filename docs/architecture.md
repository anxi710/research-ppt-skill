# Architecture: research orchestration around a production tool

```text
Sources + audience + constraints
              |
              v
Research PPT Skill (preparation)
  evidence ledger / prerequisite map / narrative
  style profile / original figures / page contracts
              |
        versioned handoff
              |
              v
ppt-master (current checkout)
  documented route / production / export / local technical checks
              |
      PPTX + build receipt
              |
              v
Research PPT Skill (independent acceptance)
  real PPTX render / content check / visual check / structural check
              |
      defect-specific repair request ----> ppt-master or preparation
              |
              v
     accepted artifacts + provenance
```

The public product is a skill and workflow, not a new model, backend, rendering service,
or monolithic automatic PDF-to-PPT script. A single tool-capable agent can hold each role
sequentially; an independent reviewer can be substituted without changing the handoff.

## Stable interface, evolving implementation

The stable boundary consists of source/evidence/asset/style/page requirements on input,
and PPTX/build provenance/repair information on output. It intentionally does not specify
a permanent upstream CLI, private Python import, SVG dialect or old route. Resolve those
from the installed backend for the current run. Do not maintain a parallel implementation.

The first successful private case inspired figure-first pages, necessary foundations,
short slide text, rich notes and all-slide rendering. Those are configurable practices,
not rules tying every new talk to its institution, topic, language, duration or page count.

## Validation scope

Unit tests cover deterministic helpers and rejection of stale/incomplete records. Real
renderer smoke tests can exercise synthetic PPTX files, without running a model. Neither
establishes end-to-end compatibility with every future ppt-master revision. Every actual
talk still requires source reading, representative pages, final rendering and review.
