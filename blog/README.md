# Blog

Create one folder per post in this directory:

```text
blog/
  my-first-post/
    index.md
    article.yml       # optional title, date and summary
    images/
      diagram.svg
  interactive-post/
    index.html
    style.css
    app.js
```

Each folder needs exactly one `index.md` or `index.html`. Use lowercase, hyphen-separated folder names. The folder name becomes the URL: `blog/my-first-post/` publishes at `https://socaity.dev/blog/my-first-post/`.

Markdown is rendered into static HTML with the site's article layout. A leading `# Heading` supplies the title. Tables, fenced code blocks, and images are supported. HTML entry files are published as complete documents, unchanged; supply your own document title, viewport, styles, and scripts.

Keep accompanying assets in the post folder and link to them relatively, for example `![Diagram](./images/diagram.svg)`. Hidden files, the Markdown entry source, and `article.yml` are not published. Other accompanying files are public.

Optional `article.yml`:

```yaml
title: My first post
date: 2026-11-19
summary: A short description for the blog index and RSS feed.
```

Without metadata, the title comes from the Markdown heading or HTML `<title>` (falling back to the folder name). Dated posts appear newest first, followed by undated posts.

Push to `main` or open a pull request from this repository to publish a live preview through the existing **Publish site** GitHub Action. The run links to the commit-specific preview. Production at `socaity.dev` updates only after approval in **Review deployments → github-pages**. After successful promotion, that preview and its temporary build artifacts are removed automatically. Fork pull requests get downloadable preview artifacts. See [publishing.md](../doc/publishing.md) for promotion and agent review. Keep drafts on a branch until ready for review.
