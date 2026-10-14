# Pre-publication validation

The generic helper layer was tested locally during preparation of this repository.

## Actually exercised

`RUN_RENDER_TESTS=1 python -m unittest discover -s tests -v` completed **22 tests**,
with zero failures and zero skips in the available Python environment.

The tests include source/contract mutation invalidation, missing evidence/style/assets,
immutable handoffs, pending review initialization, missing hidden-slide coverage, stale
backend receipts, unrelated reviewed images, source crop geometry, notes/hidden flags,
and a real LibreOffice render of a two-slide synthetic deck (one hidden backup).
The render test checks both all-slide and visible-only output and confirms that the source
PPTX bytes are unchanged. Fabricated approval records exist **only inside unit tests**;
they are not presented as actual visual reviews or scientific validation.

## Not exercised here

- End-to-end slide production with the current ppt-master implementation.
- A current upstream Git clone/update over the container's network.
- Authenticated remote repository creation or push.
- Hosted GitHub Actions and Dependabot behavior after publication.
- A new real-paper end-to-end presentation using this refactored skill.

The upstream branch and root MIT license were read through the connected GitHub reader.
The initial submodule gitlink references that observed branch head; upstream bytes are
not bundled. This is metadata verification, not production compatibility testing.

Run the local tests again in the target environment. If a real renderer is unavailable,
the renderer test is skipped unless explicitly enabled; do not describe a skipped test as
passed. A real deck still requires source reading and visual/semantic review.
