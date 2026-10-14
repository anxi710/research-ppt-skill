# Synthetic example

This example demonstrates the preparation contract, not scientific claims or an actual
paper analysis. It references no private paper, image, institution or presenter.

Run from the repository root:

```bash
python examples/synthetic/prepare.py --out ../synthetic-talk
```

The command creates two illustrative page contracts (one visible, one backup), a
synthetic source, notes and an immutable production handoff. It deliberately does not
build a PPTX: hand the resulting `handoff/run-*/handoff.md` to the current ppt-master
through your agent, then follow the review loop. Unit-test decks are generated only
inside temporary test directories and are not accepted presentation examples.
