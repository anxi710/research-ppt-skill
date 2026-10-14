# Third-party notices

## ppt-master

The optional production backend is [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master),
referenced as a real Git submodule at `third_party/ppt-master`. It is not vendored,
forked, patched, or reimplemented here. Its current root license is MIT, copyright
(c) 2025–2026 Hugo He. Its own `LICENSE` and notices remain authoritative.
Preserve those notices and any attribution required by the files actually used.

Our original orchestration instructions and helper code are also MIT. A submodule
update is not permission to strip notices or to relabel third-party assets.
If upstream changes its license, review compatibility before using or merging the update.

## Optional runtime dependencies and assets

Python packages, PDF renderers, LibreOffice, fonts, logos, images, templates, papers,
and datasets retain their own licenses. They are **not** covered by this project's
MIT license. This repository redistributes none of those packages or private assets.
The material helpers use pypdfium2 rather than bundling PyMuPDF. Upstream may use
PyMuPDF optionally; its licensing must be considered separately when redistributing
an environment or binary bundle. Consult the dependencies' actual license files.

Every research figure retains its source attribution and applicable rights. Permission
to analyze a locally supplied paper is not automatically permission to redistribute
its PDF, figures, institutional template, or logos in a public repository.
