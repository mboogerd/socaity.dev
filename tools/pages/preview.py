"""Publish immutable preview trees and wait until Pages serves their bytes."""
import argparse
from html import escape
from pathlib import Path
import re
import shutil
import time
from urllib.error import URLError
from urllib.request import urlopen


def tree(path):
    files = {}
    for entry in sorted(path.rglob("*")):
        if entry.is_symlink():
            raise ValueError(f"{entry}: preview trees cannot contain symbolic links")
        if entry.is_file():
            files[entry.relative_to(path).as_posix()] = entry.read_bytes()
    return files


def revision_path(host, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("revision must be a full Git commit SHA")
    return host / "revisions" / revision


def write_preview_index(host):
    revisions = host / "revisions"
    available = sorted(path.name for path in revisions.iterdir()
                       if path.is_dir() and re.fullmatch(r"[0-9a-f]{40}", path.name)) if revisions.exists() else []
    links = "".join(f'<li><a href="revisions/{sha}/">{escape(sha)}</a></li>' for sha in available)
    listing = f"<ul>{links}</ul>" if available else "<p>No pending previews.</p>"
    (host / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex"><title>Socaity previews</title>'
        '</head><body><h1>Socaity previews</h1>' + listing +
        '<p>Production is promoted separately after approval: '
        '<a href="https://socaity.dev/">socaity.dev</a>.</p></body></html>\n',
        encoding="utf-8")


def remove_preview(host, revision):
    target = revision_path(host, revision)
    if target.is_symlink():
        raise ValueError("a preview revision cannot be a symbolic link")
    if target.exists():
        shutil.rmtree(target)
    write_preview_index(host)


def prepare_preview(site, host, revision):
    target = revision_path(host, revision)
    if not (site / "index.html").is_file():
        raise ValueError("the preview needs index.html")
    files = tree(site)
    if target.exists():
        if tree(target) != files:
            raise ValueError(f"preview {revision} already exists with different bytes")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(site, target)
    (host / ".nojekyll").write_text("", encoding="utf-8")
    (host / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    write_preview_index(host)


def wait_for_preview(site, url, timeout=600):
    expected = {name: (site / name).read_bytes()
                for name in ("index.html", "styles.css", "app.js", "blog/index.html", "blog/feed.xml")}
    deadline = time.monotonic() + timeout
    attempt = 0
    while True:
        attempt += 1
        try:
            for name, content in expected.items():
                # An initial 404 must not stay cached after the Pages build.
                with urlopen(f"{url.rstrip('/')}/{name}?preview-check={attempt}", timeout=20) as response:
                    if response.read() != content:
                        raise ValueError(f"{name} does not match the reviewed artifact")
            print(f"Verified live preview: {url}", flush=True)
            return
        except (URLError, TimeoutError, ValueError) as error:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"Preview did not become ready: {url}") from error
            print(f"Waiting for GitHub Pages ({type(error).__name__})", flush=True)
            time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--host", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--verify-url")
    parser.add_argument("--remove", action="store_true", help="remove a successfully promoted revision")
    args = parser.parse_args()
    if args.remove and args.host and args.revision:
        remove_preview(args.host, args.revision)
    elif args.verify_url and args.site:
        wait_for_preview(args.site, args.verify_url)
    elif args.host and args.revision and args.site:
        prepare_preview(args.site, args.host, args.revision)
    else:
        parser.error("provide --site with --host and --revision or --verify-url; removal needs --remove, --host and --revision")


if __name__ == "__main__":
    main()
