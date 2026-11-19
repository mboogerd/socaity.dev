# Publishing Socaity.dev

The repository owns the homepage, blog posts and layouts, research archive, and GitHub Pages workflow. Add posts directly under `blog/`; no separate content repository, repository variable, or article access token is required.

## Writing a post

Create `blog/<slug>/index.md` or `blog/<slug>/index.html`, with any accompanying images, styles, scripts, or downloads in that same folder. Each post needs exactly one entry file. The folder name becomes its URL, for example `blog/my-first-post/index.md` publishes at `https://socaity.dev/blog/my-first-post/`.

Markdown is statically rendered with the site's article layout. A complete HTML document is copied unchanged. Both formats appear in the blog index and RSS feed. Titles come from a leading Markdown H1 or the HTML title, and optional `article.yml` can set a title, date, and summary. See [blog/README.md](../blog/README.md) for the folder structure and metadata examples.

Use relative asset links such as `./images/diagram.svg`. Hidden files, the Markdown entry source, and metadata are skipped; other accompanying files are published. Keep drafts on a branch. Merging a post into `main` creates a preview; production promotion requires approval.

## Preview and production approval

`.github/workflows/pages.yml` is the only source workflow. It tests the builders, validates and renders the research archive, and assembles one `_pages/` artifact for the exact triggering commit. The same artifact is used for preview and production; approval does not rebuild it.

- Pushes to `main` and pull requests from this repository publish a live preview at `https://mboogerd.github.io/socaity.dev-preview/revisions/<full-commit-sha>/`.
- The workflow's **preview** deployment and job summary link to the preview. The workflow verifies that its served homepage, styles, script, blog and RSS match the build bytes before it offers production promotion.
- Pull requests from forks build a downloadable `site-preview` artifact, but cannot access the preview publishing key and never deploy.
- Production only runs for `main`, after the preview succeeds and the **github-pages** environment receives approval from `mboogerd`. Administrator bypass is disabled. Self-approval is allowed so the sole maintainer can approve their own updates.
- In the source workflow run, select **Review deployments → github-pages → Approve and deploy** to promote, or **Reject** to stop it.
- An agent may inspect the exact preview and approve through GitHub's pending-deployment API when explicitly authorized by the owner. There is no unattended model that automatically approves its own changes.
- New previews can publish while earlier candidates wait for approval. Production rejects a revision if a newer commit has reached `main`; review the newest run instead.
- **Actions → Publish site → Run workflow** rebuilds manually. Build artifacts are retained for 14 days; if a candidate expires before approval, rerun the workflow.

The preview repository stores generated output only. Each commit-specific directory is immutable; attempting to replace the same revision with different bytes fails. The root preview URL links to the last published candidate. The host's `robots.txt` excludes previews from indexing. Previews are public and use a separate origin from production.

Repository variables `PREVIEW_REPOSITORY=mboogerd/socaity.dev-preview` and `PREVIEW_BASE_URL=https://mboogerd.github.io/socaity.dev-preview` identify the host. `PREVIEW_DEPLOY_KEY` is a deploy key granting write access only to that preview repository, not the production source. Removing that key/secret disables preview publication without changing production. GitHub environment protection is configured in repository settings, not just in YAML; preserve the required reviewer on **github-pages**.

Pages is configured with **Source: GitHub Actions** and the custom domain `socaity.dev`. The configured Pages URL is used for absolute RSS links. `ARTICLES_REPOSITORY` and `ARTICLES_READ_TOKEN` are no longer used.

The old blog posts and weekly digests remain removed. The blog is empty until new post folders are added. The research archive remains at `/research.html`. Retired backlog and scheduled workflows are historical material only.

## Local preview

```sh
python -m pip install -r tools/pages/requirements.txt
python -m unittest discover -s tools/pages -p 'test_*.py' -v
tools/check.sh
python tools/pages/build.py --archive site --out _pages
python -m http.server 8000 --directory _pages
```

Open `http://localhost:8000/`. Use a fresh output directory for each assembly; the build only writes it once the whole site succeeds. The builder defaults to this repository's `blog/` folder, regardless of the working directory. For a temporary preview of another folder, pass `--articles /path/to/post-folders`.
