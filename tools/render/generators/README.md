# Page generators

Every `*.py` file in this directory (except ones starting with `_`) is loaded
by `tools/render/render.py` and asked for pages. This is how `/ledger`,
`/claim` and the blog are added **without editing the renderer**.

The contract — the module-level `NAV` list, the required `generate(ctx)`
function, the keys in `ctx`, and the two rules the hook cannot enforce for you
— is the comment block marked `HOOK` near the top of
[`../render.py`](../render.py). That block is the specification; this file is a
signpost to it, so the two cannot drift apart.

Rules of thumb:

- Extend `base.html` so your page inherits the nav, footer and stylesheet. Pass
  `depth` = the number of `/` in your output path.
- Emit only paths you own. Two generators claiming one path is a build error.
- No wall clock, no `os.environ`, no network: `tools/check.sh` renders twice and
  fails on the first byte of difference.
