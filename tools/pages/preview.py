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


def prepare_preview(site, host, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("revision must be a full Git commit SHA")
    if not (site / "index.html").is_file():
        raise ValueError("the preview needs index.html")
    files = tree(site)
    target = host / "revisions" / revision
    if target.exists():
        if tree(target) != files:
            raise ValueError(f"preview {revision} already exists with different bytes")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(site, target)
    (host / ".nojekyll").write_text("", encoding="utf-8")
    (host / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (host / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex"><title>Socaity previews</title>'
        '</head><body><h1>Socaity previews</h1><p>Latest published preview: '
        f'<a href="revisions/{revision}/">{escape(revision)}</a></p>'
        '<p>Production is promoted separately after approval.</p></body></html>\n',
        encoding="utf-8")


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
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--host", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--verify-url")
    args = parser.parse_args()
    if args.verify_url:
        wait_for_preview(args.site, args.verify_url)
    elif args.host and args.revision:
        prepare_preview(args.site, args.host, args.revision)
    else:
        parser.error("provide --host and --revision, or --verify-url")


if __name__ == "__main__":
    main()
