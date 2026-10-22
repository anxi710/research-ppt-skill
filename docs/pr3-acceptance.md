# PR #3 acceptance test

This test covers the PDF import fix in [PR #3](https://github.com/anxi710/research-ppt-skill/pull/3).
The baseline is `8070d3df1f6f54b5fb60a9ae66e79c664f050212`.
The candidate is `b113d23720260c411ee47b2b05a73615f954deeb`.
The test uses synthetic data only.

The test uses a two-page synthetic PDF and a four-slide PPTX with the default Academic Navigator template.
The Python runner covers PDF import.
Actual slide production and independent review complete the test.
Do not treat the runner's `pass` as complete backend acceptance.

## Run the import test

Use a Python environment with PyMuPDF installed.
The runner uses that same interpreter for both backend versions.
Use fresh directories outside both backend checkouts.
The commands below leave the repository's submodule unchanged.

From the Research PPT Skill repository, prepare isolated checkouts:

```bash
PR3_TEST_DIR=$(mktemp -d /tmp/research-ppt-pr3.XXXXXX)
git clone --no-checkout https://github.com/hugohe3/ppt-master.git "$PR3_TEST_DIR/baseline"
git -C "$PR3_TEST_DIR/baseline" fetch origin 8070d3df1f6f54b5fb60a9ae66e79c664f050212
git -C "$PR3_TEST_DIR/baseline" checkout --detach 8070d3df1f6f54b5fb60a9ae66e79c664f050212
git clone --no-checkout https://github.com/hugohe3/ppt-master.git "$PR3_TEST_DIR/candidate"
git -C "$PR3_TEST_DIR/candidate" fetch origin b113d23720260c411ee47b2b05a73615f954deeb
git -C "$PR3_TEST_DIR/candidate" checkout --detach b113d23720260c411ee47b2b05a73615f954deeb
python scripts/test_pr3_import.py \
  --baseline "$PR3_TEST_DIR/baseline" \
  --candidate "$PR3_TEST_DIR/candidate" \
  --out "$PR3_TEST_DIR/results"
```

The runner refuses an existing output directory, dirty backends, and different commits.
It runs both attribution guards before conversion.
It runs all six upstream preservation tests without skips.
It then creates the PDF and imports it through each backend's `source_to_md.py`.

Read `results/report.json` and each version's `fidelity.json`.
The report records commands, exit codes, logs, versions, source hashes, and output hashes.
The expected table has four rows and eleven columns.
The baseline must reproduce a changed header, two rows, and ten columns.
The candidate must retain every ordered cell and exact numeric string.
The candidate must also retain the caption and the figure's RGB pixels, dimensions, axes, units, and legend.

The runner always records `end_to_end.status: pending`.
Its fixed sample does not cover scanned PDFs, all table layouts, or every backend change.
Its Markdown parser supports this fixture's flat pipe table and escaped pipes.

## Complete the slide test

Use the candidate checkout from the import test.
Read its current `AGENTS.md`, `skills/ppt-master/SKILL.md`, and selected route before production.
Use the documented Default Generate route and the actual user authorization.
Do not create simulated user confirmation files.

Complete these steps in a separate local workspace:

1. Prepare the source, evidence, figure inventory, style profile, and four-page plan through Research PPT Skill.
2. Set the page order to cover, background, table, and figure.
3. Run preparation preflight and create the immutable handoff.
4. Pass the handoff's absolute `template/` root to ppt-master as its explicit template input.
5. Install that root through the candidate's `apply_template.py` and retain its real installation receipt.
6. Create the current design spec and lock from the accepted plan and installed prototypes.
7. Run the backend's required calibration, preview, final quality gate, notes, and export steps.
8. Record the actual template mapping, backend commands, artifact hashes, and production receipt.
9. Render the exported PPTX through Research PPT Skill and inspect all four rendered slides independently.
10. Complete the parent review and final acceptance gate against the exact delivered PPTX.

For the exact parent commands, use [the runbook](runbook.md).
For the handoff fields, use [the production contract](../skills/research-ppt/references/production-handoff.md).
For review, use [the review contract](../skills/research-ppt/references/review-and-revision.md).
Keep generated PDFs, PPTX files, and rendered images outside tracked files.

Make sure that the table retains its custom headers, total row, extra column, signs, decimal places, and repeated values.
Make sure that the figure retains both series, axes, units, legend, and source identity.
Make sure that the exported deck uses the default template and preserves editable text.
Backend quality gates do not establish visual acceptance.
Title wrapping or overlap in the rendered PPTX blocks acceptance, even when PDF import passes.
Record the import verdict separately from deck layout findings.
Repair known layout faults through the backend's revision workflow and repeat the final render review.
An existing layout fault does not by itself invalidate this PR's data preservation fix.
If any required gate fails, retain the evidence and report incomplete acceptance.
Record full acceptance separately after production and independent review pass.
Do not rewrite the import report's scope or pending status.

The test does not merge the PR or change either backend.
A pass covers this synthetic case and the six upstream regression tests.
It does not establish compatibility for all papers or unrelated backend features.
Only the candidate produces a PPTX in this minimal test.
Its rendered output cannot establish whether a layout fault comes from this PR or existing backend or renderer behavior.
To identify the cause, compare the same slide inputs on both backend versions with the same fonts and renderer.
