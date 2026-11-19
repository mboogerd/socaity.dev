"""Assemble the umbrella, legacy archive, and optional article checkout."""
import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from functools import cache
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import yaml

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "doc/design/collective-intelligence"
LEGACY_URL = "https://socaity.dev/"
ATOM = "http://www.w3.org/2005/Atom"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


@cache
def markdown_renderer():
    from markdown_it import MarkdownIt

    return MarkdownIt("commonmark", {"html": False}).enable("table")


@dataclass
class Article:
    slug: str
    title: str
    date: str = ""
    summary: str = ""

    @property
    def href(self):
        return f"{self.slug}/"


class PageTitle(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def public_entries(folder):
    for entry in sorted(folder.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_symlink():
            raise ValueError(f"{entry}: symbolic links cannot be published")
        yield entry


def copy_assets(source, target):
    target.mkdir(exist_ok=True)
    for entry in public_entries(source):
        destination = target / entry.name
        if entry.is_dir():
            copy_assets(entry, destination)
        else:
            shutil.copyfile(entry, destination)


def publish_article(source, target, template):
    slug = source.name
    if not SLUG.fullmatch(slug):
        raise ValueError(f"{source}: use a lowercase, hyphen-separated slug")

    entries = {entry.name: entry for entry in public_entries(source)}
    indexes = [entries[name] for name in ("index.md", "index.html") if name in entries]
    if len(indexes) != 1 or not indexes[0].is_file():
        raise ValueError(f"{source}: expected exactly one index.md or index.html")
    index = indexes[0]
    metadata_file = entries.pop("article.yml", None)
    metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) if metadata_file else {}
    if not isinstance(metadata, dict) or metadata.keys() - {"title", "date", "summary"}:
        raise ValueError(f"{source}: article.yml must contain only title, date and summary")
    for key in ("title", "summary"):
        if key in metadata and not isinstance(metadata[key], str):
            raise ValueError(f"{source}: {key} must be a string")
    published = str(metadata["date"]) if "date" in metadata else ""
    if "date" in metadata:
        try:
            if date.fromisoformat(published).isoformat() != published:
                raise ValueError
        except ValueError:
            raise ValueError(f"{source}: date must use YYYY-MM-DD") from None

    raw = index.read_text(encoding="utf-8")
    markdown = index.name == "index.md"
    if markdown:
        renderer = markdown_renderer()
        context = {}
        tokens = renderer.parse(raw, context)
        inferred = ""
        if tokens and tokens[0].tag == "h1":
            inferred = "".join(token.content for token in tokens[1].children)
        title = metadata.get("title") or inferred or slug.replace("-", " ").capitalize()
        if inferred:
            tokens = tokens[3:]
        body = renderer.renderer.render(tokens, renderer.options, context)
    else:
        title_parser = PageTitle()
        title_parser.feed(raw)
        title = metadata.get("title") or "".join(title_parser.parts).strip() or slug.replace("-", " ").capitalize()

    article = Article(slug, title, published, metadata.get("summary", ""))
    target.mkdir()
    if markdown:
        (target / "index.html").write_text(template.render(article=article, body=Markup(body)), encoding="utf-8")
    else:
        shutil.copyfile(index, target / "index.html")
    for entry in entries.values():
        if entry == index:
            continue
        destination = target / entry.name
        if entry.is_dir():
            copy_assets(entry, destination)
        else:
            shutil.copyfile(entry, destination)
    return article


def update_feed(path, articles, base_url):
    ET.register_namespace("atom", ATOM)
    feed = ET.parse(path)
    channel = feed.getroot().find("channel")
    channel.find("link").text = base_url + "blog/"
    channel.find("description").text = "Articles and project updates from Socaity."
    channel.find(f"{{{ATOM}}}link").set("href", base_url + "blog/feed.xml")
    latest = channel.find("pubDate")
    if latest is not None:
        channel.remove(latest)
    archive = []
    for item in channel.findall("item"):
        link = item.find("link")
        slug = link.text.removeprefix(LEGACY_URL + "blog/").rstrip("/")
        link.text = base_url + "blog/" + slug + "/"
        guid = item.find("guid")
        if guid.text != link.text:
            guid.set("isPermaLink", "false")
        archive.append(Article(slug, item.findtext("title"), item_date(item), item.findtext("description", "")))
    for article in articles:
        item = ET.SubElement(channel, "item")
        url = base_url + "blog/" + article.href
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", isPermaLink="true").text = url
        if article.summary:
            ET.SubElement(item, "description").text = article.summary
        if article.date:
            stamp = datetime.fromisoformat(article.date).replace(tzinfo=timezone.utc)
            ET.SubElement(item, "pubDate").text = format_datetime(stamp, usegmt=True)

    items = channel.findall("item")
    for item in items:
        channel.remove(item)
    items.sort(key=lambda item: (item_date(item), item.findtext("link")), reverse=True)
    if items and (published := items[0].findtext("pubDate")):
        ET.SubElement(channel, "pubDate").text = published
    channel.extend(items)
    feed.write(path, encoding="utf-8", xml_declaration=True)
    return archive


def item_date(item):
    published = item.findtext("pubDate")
    return parsedate_to_datetime(published).date().isoformat() if published else ""


def assemble(archive, output, articles_root, base_url):
    templates = Environment(loader=FileSystemLoader(Path(__file__).parent),
                            autoescape=select_autoescape(), keep_trailing_newline=True)
    with TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary) / "site"
        shutil.copytree(archive, stage)
        blog = stage / "blog"
        (stage / "index.html").rename(stage / "research.html")
        (blog / "index.html").rename(blog / "archive.html")
        for filename in ("index.html", "styles.css", "app.js"):
            shutil.copyfile(DESIGN / filename, stage / filename)
        shutil.copyfile(Path(__file__).with_name("blog.css"), blog / "blog.css")

        articles = []
        if articles_root is not None:
            template = templates.get_template("article.html")
            reserved = {entry.name.casefold() for entry in blog.iterdir()}
            for folder in public_entries(articles_root):
                if folder.is_dir():
                    if folder.name.casefold() in reserved:
                        raise ValueError(f"{folder}: URL already exists in the archive")
                    articles.append(publish_article(folder, blog / folder.name, template))
        archive_articles = update_feed(blog / "feed.xml", articles, base_url)
        all_articles = sorted(articles + archive_articles,
                              key=lambda article: (article.date, article.slug), reverse=True)
        (blog / "index.html").write_text(
            templates.get_template("index.html").render(articles=all_articles), encoding="utf-8")
        stage.rename(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="existing legacy render")
    parser.add_argument("--out", required=True, type=Path, help="new output directory")
    parser.add_argument("--articles", type=Path, help="articles/ from the content repository")
    parser.add_argument("--base-url", default=LEGACY_URL, help="absolute Pages URL for RSS")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    url = urlsplit(base_url)
    if url.scheme not in ("http", "https") or not url.netloc or url.query or url.fragment:
        parser.error("--base-url must be an absolute HTTP(S) site URL")
    if args.out.exists() or args.out.resolve().is_relative_to(args.archive.resolve()):
        parser.error("--out must be a new directory outside --archive")
    try:
        assemble(args.archive, args.out, args.articles, base_url)
    except (OSError, ValueError, yaml.YAMLError) as error:
        parser.exit(1, f"Pages build failed: {error}\n")


if __name__ == "__main__":
    main()
