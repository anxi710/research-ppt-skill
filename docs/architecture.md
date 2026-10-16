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

The presentation can integrate papers, project reports, reading notes and user results
around one research question. The brief records type/depth, evidence retains source
roles and locators, and the slide plan records coverage and the timed main/backup split.
Detailed explanation is distributed across readable slides and speaker notes. A
single-paper talk is an explicit supported mode rather than the only input model.

## Stable interface, evolving implementation

The stable boundary consists of source/evidence/asset/style/page requirements on input,
and PPTX/build provenance/repair information on output. The `ppt-master` submodule tracks
upstream `main`. Before each new production job, check for updates, resolve its real local
path and read the current entry instructions. Follow that checkout's production route and
record the actual revision used; keep it unchanged during the job. The backend owns its
production and export implementation.

New workspaces record a design-contract version so missing current policies cannot
silently turn them into legacy jobs. The default Academic Navigator template is
selected explicitly, copied into the immutable handoff and passed as an exact
workspace root to the backend. Installed-file provenance and independent rendered
page review check its application. User-requested alternatives are recorded as
overrides; saved legacy contracts remain supported.

The first successful private case inspired figure-first pages, necessary foundations,
short slide text, rich notes and all-slide rendering. Those are configurable practices,
not rules tying every new talk to its institution, topic, language, duration or page count.

## Validation scope

Unit tests cover deterministic helpers and rejection of stale/incomplete records. Real
renderer smoke tests can exercise synthetic PPTX files, without running a model. Neither
establishes end-to-end compatibility with every future ppt-master revision. Every actual
talk still requires source reading, representative pages, final rendering and review.
