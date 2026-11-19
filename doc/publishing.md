# Publishing Socaity.dev

The site repository owns the collective-intelligence homepage, its styles and interactions, the blog layout, and the Pages workflow. A second repository owns the articles. GitHub Actions builds one static site from the two sources. The homepage links to the research archive, and the blog index and RSS feed include both the new articles and the existing posts and weekly digests.

## Article folders

Use an `articles/` directory at the root of the content repository. Give each article a stable lowercase slug and one entry file.

| File in the content repository | Published result |
| --- | --- |
| `articles/what-we-can-build/index.md` | `/blog/what-we-can-build/` using the Socaity article layout |
| `articles/a-living-map/index.html` | `/blog/a-living-map/` using the author's complete HTML document |
| `articles/a-living-map/map.css` | `/blog/a-living-map/map.css` |
| `articles/a-living-map/images/map.png` | `/blog/a-living-map/images/map.png` |

Link to assets using relative URLs such as `./map.css` and `./images/map.png`. This works on both the custom domain and the GitHub project URL. Markdown supports images, fenced code, and tables. Use `index.html` when the article needs custom markup or styles. A full HTML article is served as written, including any scripts, so merge it as carefully as a change to the main site. Include `<html lang="en">` or the article's language, a descriptive title, and a viewport meta tag in standalone HTML. A link back to the blog uses `../`.

The blog index takes the title from a leading Markdown H1 or the HTML `<title>`. To override it or add a date and summary, put an optional `article.yml` next to the entry file.

```yaml
title: A living map
date: 2026-11-19
summary: How a group can connect its needs to tools it can make together.
```

Dated articles appear newest first, followed by undated articles. Keep drafts on a branch. The content repository's default branch is the publication source, and files in a published article folder can be downloaded. The build skips hidden files and the entry Markdown and metadata files.

## GitHub setup

1. Create the article repository, for example `mboogerd/socaity-articles`, with an `articles/` folder containing the first article.
2. In the site repository, set **Settings → Pages → Source** to **GitHub Actions**. Set the custom domain there and configure DNS if you want to serve the site on `socaity.dev`. The workflow reads the configured Pages URL for RSS.
3. Under **Settings → Secrets and variables → Actions → Variables**, set `ARTICLES_REPOSITORY` to the content repository's `owner/name`. For a private content repository, add an `ARTICLES_READ_TOKEN` secret with **Contents: read** access to that repository.
4. Every push to `main` publishes the site through **Actions → Publish site** (`pages.yml`). Use **Run workflow** to rebuild manually. Check the homepage and `/blog/` from the deployment URL shown in the run. The setup also supports deploying the homepage and existing archive before an article repository is configured.

To publish automatically on article changes, add this workflow to the content repo at `.github/workflows/rebuild-site.yml`. Set its `SITE_DEPLOY_TOKEN` secret to a fine-grained token with **Actions: write** for the site repository. This grants the workflow authority to start the site rebuild. Adjust the content branch and site repository values if yours differ.

```yaml
name: Rebuild Socaity.dev
on:
  push:
    branches: [main]
    paths: ['articles/**']

permissions: {}

jobs:
  rebuild:
    runs-on: ubuntu-latest
    steps:
      - name: Start the Pages build
        env:
          GH_TOKEN: ${{ secrets.SITE_DEPLOY_TOKEN }}
          GH_REPO: mboogerd/socaity.dev
        run: gh workflow run pages.yml --ref main
```

Each update to the website's `main` branch or an article push with the rebuild workflow enabled triggers a build. `pages.yml` is the only active workflow; the older graph checks, drift alarms, and scheduled weekly digest workflows have been retired. Existing posts and weekly digests remain available in the archive.

## Local preview

Run from the site repository with the content repository checked out beside it.

```sh
python -m pip install -r tools/pages/requirements.txt
tools/check.sh
python tools/pages/build.py --archive site --out _pages --articles ../socaity-articles/articles
python -m http.server 8000 --directory _pages
```

Open `http://localhost:8000/`. Omit `--articles` to preview only the site and its existing archive. Use a fresh output directory for each build. The assemble command writes the new directory only once the full site is ready.
