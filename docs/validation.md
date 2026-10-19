# Validation status

The generic helper layer is tested locally with synthetic inputs. These checks are
separate from backend production, hosted CI and a real presentation's acceptance.

## Previously recorded helper checks

Using the selected conda `docs` environment,
`python -m unittest discover -s tests -v` completed **60 tests**: **59 passed** and
the opt-in real-renderer test was skipped. `python scripts/check_repo.py` and the
skill frontmatter validator also passed.

The tests cover proposed presentation type/depth, explicit overrides, stale depth
acceptance, unchanged legacy briefs and mixed-material synthesis provenance through
handoff, as well as request-directory output defaults, Unicode project names, collision
preservation, explicit path overrides, named delivery handoffs, invalid inputs leaving
no default workspace, pending or stale intake records, explicit delegation, Q&A reservations,
source/contract mutation invalidation, missing evidence/style/assets, immutable handoffs,
pending reviews, missing backup-slide review coverage, stale backend receipts, unrelated
reviewed images, source crop geometry, and notes/hidden flags. Version checks reject
invalid SemVer and mismatched skill metadata, badge text/image URLs or changelog entries.

Fictional intake records in synthetic tests/examples illustrate the contract; fabricated
final-deck review records exist only inside unit tests. Neither represents actual user
approval, visual review or scientific validation.

A separate preparation-only synthetic trial used a reference report, a pilot-result
CSV and an interpretive note. It produced an integrated plan with source-qualified
comparisons, explicit gaps, notes and hidden backups. The deliberately short materials
supported a 900-second main plan against a requested 1500-second speaking budget;
preflight failed on timing and production remained blocked. The trial did not fill the
gap with invented findings, shorten the accepted budget or claim a finished deck.
This is evidence about that preparation scenario, not end-to-end PPTX generation.

## Hosted CI evidence

The [main push run](https://github.com/anxi710/research-ppt-skill/actions/runs/38711659610)
for commit `9700b8e91afa81c953fb276401d11445fb8eb63f` passed with
`actions/checkout@v7`, `actions/setup-python@v7` and Python **3.11.17**.
It completed **44 tests**: **43 passed** and the opt-in renderer test was skipped;
`python scripts/check_repo.py` also passed.

This confirms the two action upgrades work together for that revision's main push
workflow. It does not cover the additional local changes awaiting a push or every
hosted workflow and Dependabot operation.

## Automated real-renderer regression

The `render` job in [ci.yml](../.github/workflows/ci.yml) runs on Ubuntu 24.04 with
Python 3.11, installs `libreoffice-impress`, `fonts-noto-cjk` and `fonts-liberation`,
prints the renderer version and font matches, and sets `RUN_RENDER_TESTS=1`.
It runs `test_decktools.RenderTests` explicitly. Missing LibreOffice is an error
when rendering is requested; the ordinary unit job still skips these opt-in tests.
The install step follows GitHub's [Ubuntu runner package guidance](https://docs.github.com/en/actions/how-tos/manage-runners/github-hosted-runners/customize-runners).

| Layer | Automated coverage | What it cannot establish |
|---|---|---|
| Structure/contract | Existing `test_default_design.py` and `test_visual_contract.py`: default Latin/CJK font declarations, role sizes, section IDs, main-only navigation, hidden backups, immutable template provenance and pending review gates. PPTX audit checks notes, hidden flags and plan alignment. | Actual installed fonts or faithful application of the template to the final slide. |
| Real render | LibreOffice opens synthetic native PPTX files and exports PDF; PDFium produces nonblank PNGs. Tests verify both hidden-page modes, source immutability, ordered slide mapping, Chinese/English text and navigation-label survival, page dimensions, output names/counts, and report/manifest hashes. A backup between visible slides exercises non-contiguous mapping `[1, 2, 4]`. | Exact typography, active-tab appearance, overlap, clipping, aesthetics, projection readability, or scientific correctness. |
| Final visual/semantic review | Remains pending; no render test marks a deck visually approved. | Requires a reviewer to inspect final-PPTX page images (including backups), confirm fonts and navigation, and judge readability, layout and claims against the sources. |

The mixed-script deck uses the initialized default style/plan and explicit Latin/CJK
runs with synthetic navigation labels. It is constructed with `python-pptx`, **not**
produced by ppt-master from the Academic Navigator SVG package. Existing contract
tests cover the template snapshot and provenance; this render smoke test does not
certify the backend's current template conversion or v0.4.1's final appearance.
No model, image API, paid service, source paper or proprietary font is used.

### Run locally

On Ubuntu/Debian, install the renderer and open fonts (once):

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends -y libreoffice-impress fonts-noto-cjk fonts-liberation
python -m pip install -r requirements.txt
libreoffice --version
fc-match 'Times New Roman'
fc-match 'Microsoft YaHei'
RUN_RENDER_TESTS=1 PYTHONPATH=tests python -m unittest test_decktools.RenderTests -v
RUN_RENDER_TESTS=1 python -m unittest discover -s tests -v
python scripts/check_repo.py
```

Microsoft YaHei and Times New Roman may be absent on Linux. Fontconfig can substitute
Noto CJK/Liberation or other installed fonts. Tests check Unicode text survival, not
pixel equality or font metrics; the Chinese assertion explains the CJK-font prerequisite.
Missing Chinese text/glyphs requires checking installed fonts before blaming code.
Successful text extraction alone does not prove correct glyph appearance. Keep font
differences in the review record; do not copy proprietary font binaries into the repo.

Set `RENDER_TEST_ARTIFACTS=/tmp/research-ppt-render-evidence` on the render command to
retain synthetic workspaces, source decks, PDFs, page PNGs, audit/render reports and
renderer logs, including partial output after an assertion failure. CI uploads these
as `synthetic-pptx-render` for seven days, even on test failure. Without this variable,
temporary fixtures are deleted. The upload is limited to these synthetic test folders.
These artifacts are inspection/debugging evidence, not automatic visual acceptance.

An earlier recorded suite completed **23 tests**, including the original renderer
test, with zero failures or skips. That is historical evidence; use the current
revision's logs to establish whether its real-render tests actually ran.

## Outside these checks

- End-to-end slide production with the current ppt-master implementation.
- Upstream Git clone/update over the network.
- Hosted workflow paths and Dependabot operations beyond the run recorded above.
- A real-paper end-to-end presentation using this skill.

The configured upstream branch, recorded gitlink and license observations document
backend provenance. They do not certify current production compatibility; a new job still
reads the actual checkout's instructions and validates representative pages.

Run the local tests again in the target environment. If a real renderer is unavailable,
the renderer test is skipped unless explicitly enabled; do not describe a skipped test as
passed. A real deck still requires source reading and visual/semantic review.
