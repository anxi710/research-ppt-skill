# Synthetic example

This example demonstrates the preparation contract, not scientific claims or an actual
paper analysis. It references no private paper, image, institution or presenter.
Its intake records are fictional fixtures for demonstrating the contract, not evidence
of actual user approval. Real work must capture the user's actual acceptance or delegation.

Run from the repository root; all relative paths below use that directory:

```bash
python examples/synthetic/prepare.py --out outputs/synthetic-talk
```

Open `outputs/synthetic-talk/brief.json` to inspect a real generated workspace brief.
This file is created at the `--out` workspace root, not the repository root. The
example generator uses a short, two-minute synthetic plan and fictional intake
acceptance so it can demonstrate a handoff without a real conversation.
The demo's fixed fixture names are not semantic naming. For a real talk, the agent
summarizes the topic and uses `workflow.py init --name <project-name>` to create
`outputs/<project-name>/` with matching delivery filenames under `exports/`.
The defaults are `<project-name>.pptx`, `<project-name>-preview.pdf` (visible-slide
render) and `<project-name>-notes.md`; this preparation-only demo creates none of them.

A separate [pending brief example](../../skills/research-ppt/templates/brief.example.json)
shows a 25-minute session with 5 minutes reserved for Q&A. It uses the same synthetic
source bytes, but keeps confirmation pending and does not contain a prepared slide
plan. Use the [runbook field guide](../../docs/runbook.md#1-confirm-requirements-and-initialize-a-workspace)
to adapt requirements while keeping actual source fingerprints from `init`.

The command uses the current design contract: a cover, a visible example page and
a hidden backup, with planned navigation and an explicitly selected default template.
The immutable handoff includes the template snapshot and fingerprints; actual template
application and rendered-page review remain pending production. It also creates a
synthetic source and planned notes. It deliberately does not
build a PPTX: hand the resulting `handoff/run-*/handoff.md` to the current ppt-master
through your agent, then follow the review loop. Unit-test decks are generated only
inside temporary test directories and are not accepted presentation examples.
