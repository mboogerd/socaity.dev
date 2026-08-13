#!/usr/bin/env python3
"""Open exactly one GitHub Discussions thread per weekly digest, linking home.

council/socaity-ue3: the digest is canonical on the blog, and GitHub Discussions
is the single community channel -- "one artifact, one conversation venue". So
this step opens one thread whose body is a pointer, never a copy: the words live
on the blog, the argument lives in the thread.

Exactly one, enforced by a file rather than by hope: blog/discussions.json maps
a post slug to the thread that was opened for it. A slug already present is
skipped, so a re-run of the workflow cannot open a second thread. The renderer
reads that same file to show a "discussion thread" link in the register, which
is why the file is committed rather than kept in a workflow output.

GitHub Discussions has no REST create endpoint; creation is the GraphQL
`createDiscussion` mutation, which needs two node IDs looked up first. Verified
against the GitHub documentation (see docs/ references in the comments below):

  POST https://api.github.com/graphql
  Authorization: bearer <token>
  https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
  https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions

  mutation {
    createDiscussion(input: {repositoryId: "...", categoryId: "...",
                             body: "...", title: "..."}) {
      discussion { id }
    }
  }

A workflow calling this needs `permissions: discussions: write` (documented
scope in the Actions workflow-syntax reference).

Usage:
  python3 tools/blog/announce_digest.py --post blog/posts/2026-W33-ledger-digest.md
  python3 tools/blog/announce_digest.py --week 2026-W33 --dry-run

  --dry-run prints the exact GraphQL documents and variables and calls nothing,
  which is the only way this file can be exercised without a live repository.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"
SITE = "https://socaity.dev/"
REGISTRY = os.path.join("blog", "discussions.json")

LOOKUP = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id
    discussionCategories(first: 25) { nodes { id name } }
  }
}
"""

CREATE = """
mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
  createDiscussion(input: {repositoryId: $repositoryId, categoryId: $categoryId,
                           title: $title, body: $body}) {
    discussion { id url }
  }
}
"""


def call(token, query, variables):
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(API, data=payload, method="POST", headers={
        "Authorization": "bearer %s" % token,
        "Content-Type": "application/json",
        "User-Agent": "socaity.dev-digest-announcer",
    })
    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # The body is where GitHub explains itself ("Resource not accessible by
        # integration", "Discussions are disabled"), and urlopen throws it away
        # unless it is read here. This step has never run against the live API,
        # so the first person to see it fail must get the real message.
        detail = error.read().decode("utf-8", "replace").strip()
        raise SystemExit("announce: HTTP %s from %s: %s"
                         % (error.code, API, detail or "<empty body>"))
    if body.get("errors"):
        raise SystemExit("announce: GraphQL error: %s" % json.dumps(body["errors"]))
    if body.get("data") is None:
        raise SystemExit("announce: GraphQL returned no data: %s" % json.dumps(body))
    return body["data"]


def read_header(path):
    header = {}
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    if not lines or lines[0].strip() != "---":
        raise SystemExit("announce: %s has no --- header" % path)
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep:
            header[key.strip()] = value.strip()
    return header


def thread_body(slug, header):
    """A pointer, not a copy. The post is the artifact; this is the doorway."""
    url = SITE + "blog/" + slug + "/"
    return "\n".join([
        header.get("summary", ""),
        "",
        "Read it here: %s" % url,
        "",
        "This digest was written by a program from the commit history of the "
        "repository and from the contribution record, and committed unedited. "
        "The command that produced it is printed on the post.",
        "",
        "This thread is opened automatically, one per digest. Corrections to "
        "the digest are corrections to the program or to the history it reads "
        "— say so here and it becomes an issue.",
    ])


def load_registry(root):
    path = os.path.join(root, REGISTRY)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save_registry(root, data):
    path = os.path.join(root, REGISTRY)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--post", help="path to the digest post file")
    ap.add_argument("--week", help="ISO week, when the post path is the default one")
    ap.add_argument("--category", default="Announcements",
                    help="Discussions category name (default: Announcements)")
    ap.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""),
                    help="owner/name (default: $GITHUB_REPOSITORY)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the calls that would be made and exit 0")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    post = args.post
    if not post:
        if not args.week:
            raise SystemExit("announce: pass --post or --week")
        post = os.path.join("blog", "posts", "%s-ledger-digest.md" % args.week)
    path = os.path.join(root, post)
    if not os.path.isfile(path):
        raise SystemExit("announce: no such post: %s" % post)

    slug = os.path.basename(post)[:-3]
    header = read_header(path)
    title = "%s (discussion)" % header.get("title", slug)
    body = thread_body(slug, header)

    registry = load_registry(root)
    if slug in registry:
        print("announce: %s already has a thread: %s" % (slug, registry[slug]))
        return 0

    owner, _, name = args.repository.partition("/")
    if not (owner and name) and not args.dry_run:
        raise SystemExit("announce: set --repository owner/name or $GITHUB_REPOSITORY")

    if args.dry_run:
        print("POST %s" % API)
        print("Authorization: bearer <token>   # $GITHUB_TOKEN, discussions: write")
        print("--- lookup ---")
        print(json.dumps({"query": LOOKUP,
                          "variables": {"owner": owner or "<owner>",
                                        "name": name or "<name>"}}, indent=2))
        print("--- create (ids filled in from the lookup response) ---")
        print(json.dumps({"query": CREATE, "variables": {
            "repositoryId": "<repository.id>",
            "categoryId": "<id of category %r>" % args.category,
            "title": title, "body": body}}, indent=2))
        print("--- then written to %s ---" % REGISTRY)
        print(json.dumps(dict(registry, **{slug: "<discussion.url>"}),
                         indent=2, sort_keys=True))
        return 0

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("announce: $GITHUB_TOKEN is not set")

    data = call(token, LOOKUP, {"owner": owner, "name": name})
    repository = data.get("repository")
    if repository is None:
        raise SystemExit("announce: the token cannot see %s/%s" % (owner, name))
    categories = {node["name"]: node["id"]
                  for node in repository["discussionCategories"]["nodes"]}
    if not categories:
        # An empty category list is what a repository with Discussions switched
        # off looks like through this query -- not a missing category.
        raise SystemExit(
            "announce: %s/%s reports no Discussions categories at all, which is "
            "what Discussions being switched off looks like. Enable it under "
            "Settings > General > Features > Discussions." % (owner, name))
    if args.category not in categories:
        raise SystemExit("announce: no Discussions category %r (have: %s)"
                         % (args.category, ", ".join(sorted(categories))))

    created = call(token, CREATE, {
        "repositoryId": repository["id"],
        "categoryId": categories[args.category],
        "title": title,
        "body": body,
    })
    url = created["createDiscussion"]["discussion"]["url"]
    registry[slug] = url
    save_registry(root, registry)
    print("announce: opened %s" % url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
