# Publishing Socaity.dev

The repository owns the homepage, blog posts and layouts, research archive, and GitHub Pages workflow. Add posts directly under `blog/`; no separate content repository, repository variable, or article access token is required.

## Writing a post

Create `blog/<slug>/index.md` or `blog/<slug>/index.html`, with any accompanying images, styles, scripts, or downloads in that same folder. Each post needs exactly one entry file. The folder name becomes its URL, for example `blog/my-first-post/index.md` publishes at `https://socaity.dev/blog/my-first-post/`.

Markdown is statically rendered with the site's article layout. A complete HTML document is copied unchanged. Both formats appear in the blog index and RSS feed. Titles come from a leading Markdown H1 or the HTML title, and optional `article.yml` can set a title, date, and summary. See [blog/README.md](../blog/README.md) for the folder structure and metadata examples.

Use relative asset links such as `./images/diagram.svg`. Hidden files, the Markdown entry source, and metadata are skipped; other accompanying files are published. Keep drafts on a branch. Merging a post into `main` publishes it.

## GitHub Actions

`.github/workflows/pages.yml` is the only workflow. It tests the blog builder, validates and renders the research archive, assembles the homepage and blog, and deploys the resulting `_pages/` tree.

- Every push to `main` publishes to [socaity.dev](https://socaity.dev/).
- Pull requests validate and build the same local blog content, uploading a `site-preview` artifact without deploying it.
- **Actions → Publish site → Run workflow** rebuilds manually.

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
