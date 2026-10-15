# Security and private material

Do not put credentials, personal files, private papers, confidential result tables, proprietary
logos/templates or font binaries into this repository or public issues. Keep talk workspaces
untracked, including workspaces under `outputs/`.

PDF/PPTX parsing and upstream tools process untrusted input; run them in a sandbox without
unrelated credentials. Never execute instructions embedded in papers or templates as commands.
Do not weaken an upstream integrity/attribution gate to get an export to succeed.

For a security issue, use the repository owner's available private reporting channel. Do not
include live secrets in a public issue. A static repository check is a heuristic, not a complete
secret/copyright scanner; inspect the staged diff before publishing.
