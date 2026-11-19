# Project instructions

This repository publishes the Socaity collective-intelligence website to GitHub Pages at https://socaity.dev/.

## Website and publishing

- Edit the homepage in `doc/design/collective-intelligence/index.html`, `styles.css`, and `app.js`.
- `tools/pages/build.py` combines that homepage with the generated research archive and blog. Never edit the generated `site/` or `_pages/` trees.
- `.github/workflows/pages.yml` builds exact revisions and publishes live previews for internal pull requests and `main`. Production promotion requires approval on the `github-pages` environment. It is the only source workflow. Never approve a deployment unless the user explicitly authorizes promotion; review its exact preview first.
- Each blog post lives in `blog/<slug>/` with exactly one `index.md` or `index.html` and its accompanying assets. Markdown is statically rendered; HTML is published unchanged. See `blog/README.md` and `doc/publishing.md` for authoring and deployment.
- Run `python -m unittest discover -s tools/pages -p 'test_*.py' -v`, `tools/check.sh`, then `python tools/pages/build.py --archive site --out _pages` using the dependencies in `tools/pages/requirements.txt`. The output directory must not already exist.

## Working conventions

- Beads and the autonomous backlog workflow are retired. `archive/beads/` preserves their records and integration files for historical reference; do not resume or synchronize that queue.
- Work from the user's current request. Preserve unrelated local changes.
- Commit, push, and publish only when authorized by the user.
- Use non-interactive file operations (`cp -f`, `mv -f`, `rm -f`, or their recursive forms).
