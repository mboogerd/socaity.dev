"""/claim — the page a merged contributor lands on, and its two companions.

council/socaity-ipg.md clause 3.  The three `ssh-keygen` blocks below are the
single source of truth for the flow: the page renders them, and
`tools/claim/test_claim_flow.sh` imports this module and *runs* them.  A
copy-paste block that does not run is the failure mode of this whole surface,
so nothing here is retyped anywhere else.

Pages emitted:
  claim/index.html                the three steps
  claim/reserved/index.html       what an entry permalink shows before and
                                  after the claim ("attribution reserved")
  claim/merge-comment/index.html  doc/templates/merge-comment.md, verbatim

Determinism: no wall clock.  The one derived duration on the page comes from
the published parameter set and the validator's V, not from today's date.
"""

import os
import sys

# No NAV export, on purpose (council/socaity-0hb.md §I, and the note above
# SURFACES in render.py). This generator emits three pages and claims no nav
# entry: /claim is reached from the reasons to claim it — the unclaimed-ticket
# line on a node page, every row of the /roadmap work list, the empty second
# row of the ledger, the FAQ, and the merge comment on the pull request that
# earned the entry — not from a table of contents. Adding a NAV entry back
# would not merely add a link, it would re-publish the surface into the global
# masthead on every page.

#: The command file the contributor's key lives in.  One directory, three
#: files, all of it under the contributor's own $HOME.
KEY_PATH = "~/.socaity/claim-key"

#: The sshsig namespace.  It is part of what is signed, so a signature made
#: for socaity cannot be replayed as an SSH login or a git commit signature.
NAMESPACE = "socaity.dev/claim"

#: The account placeholder the contributor edits.  Deliberately shouty: an
#: unedited placeholder must fail loudly at step 2, not silently at step 3.
LOGIN_PLACEHOLDER = "YOUR-GITHUB-LOGIN"

# ---------------------------------------------------------------------------
# THE THREE BLOCKS.  Every one of these is executed verbatim by
# tools/claim/test_claim_flow.sh, with two documented substitutions: the login
# placeholder, and `-N ''` appended to step 1 so the test is not blocked on
# the passphrase prompt a human should answer.
# ---------------------------------------------------------------------------
STEPS = [
    {
        "n": 1,
        "title": "Make a key",
        "commands": [
            'mkdir -p ~/.socaity && ssh-keygen -t ed25519 -f %s -C "socaity claim"'
            % KEY_PATH,
        ],
        # The `why` of every step is rendered ABOVE its command block, never
        # under it (council/socaity-0hb.md §C: a reassurance sentence is never
        # smaller, greyer or LOWER than the command it accompanies).  The
        # tenses below are written for that order and only for it.
        "why": (
            "The command below writes two files. <code>claim-key</code> is the "
            "private half: it "
            "stays on your machine, and nothing on this site, in this repository, or "
            "in the record ever asks you for it. <code>claim-key.pub</code> is the "
            "public half — that half becomes your name on the record. ssh-keygen "
            "asks for a passphrase; use one, and read the note on backing it up "
            "before you close the terminal."),
    },
    {
        "n": 2,
        "title": "Sign one line",
        "edit": (
            "Replace <code>%s</code> with your account name — the one that authored "
            "the merged pull request — then run both lines." % LOGIN_PLACEHOLDER),
        "commands": [
            "printf 'link:github:%%s:%%s\\n' %s \\\n"
            "  \"$(cut -d' ' -f1,2 %s.pub)\" > ~/.socaity/claim.txt"
            % (LOGIN_PLACEHOLDER, KEY_PATH),
            "ssh-keygen -Y sign -n %s -f %s ~/.socaity/claim.txt"
            % (NAMESPACE, KEY_PATH),
        ],
        "why": (
            "The line the first command writes says: this account and this key are "
            "the same person. Signing it proves one direction of that — only the "
            "private key you made a moment ago can produce that signature, and it "
            "can only be used for a socaity claim, never as a login or a commit "
            "signature."),
    },
    {
        "n": 3,
        "title": "Publish it",
        "commands": [
            "cat ~/.socaity/claim.txt ~/.socaity/claim.txt.sig",
        ],
        "why": (
            "The command below prints the two files you just made. Paste everything "
            "it prints as a comment on your merged pull request. "
            "Publishing it there proves the other direction — only your account can "
            "post as your account. Neither half is worth anything alone; together "
            "they are the whole claim, and nobody else can produce both."),
    },
]

#: Verification, for the maintainer and for any stranger auditing the record.
#: Every path is absolute under ~/.socaity: the three steps above leave the
#: files there, and this block must run from whatever directory the reader
#: happens to be in -- a verify block that only works after an undocumented
#: `cd` is a block that does not work.
VERIFY_SSH = [
    'printf \'%%s namespaces="%s" %%s\\n\' "github:%s" \\\n'
    '  "$(cut -d\' \' -f1,2 %s.pub)" > ~/.socaity/allowed_signers'
    % (NAMESPACE, LOGIN_PLACEHOLDER, KEY_PATH),
    "ssh-keygen -Y verify -f ~/.socaity/allowed_signers -I github:%s -n %s \\\n"
    "  -s ~/.socaity/claim.txt.sig < ~/.socaity/claim.txt"
    % (LOGIN_PLACEHOLDER, NAMESPACE),
]

#: Reads the same two files rather than a `pasted-comment.txt` that no step on
#: the page ever creates.
VERIFY_REPO = [
    "cat ~/.socaity/claim.txt ~/.socaity/claim.txt.sig \\\n"
    "  | python3 tools/claim/verify_claim.py --login %s" % LOGIN_PLACEHOLDER,
]

#: `tr` because the binding is fixed by the maintainer from the pull request
#: author's login and by the contributor from what they typed at step 2.  A
#: GitHub login is case-insensitive, so the two only agree if both sides fold
#: case; verify_claim.py folds it the same way.
RECOMPUTE = [
    "printf 'github:%s' " + LOGIN_PLACEHOLDER
    + " | tr 'A-Z' 'a-z' | shasum -a 256",
]

MERGE_COMMENT_SOURCE = "doc/templates/merge-comment.md"
REPO_BLOB = "https://github.com/socaity/socaity.dev/blob/main/"


#: Prose spells small numbers; the drift check has to accept either spelling.
_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve"
          .split())


def _word(n):
    return _WORDS[n] if 0 <= n < len(_WORDS) else str(n)


def _months_until_adjudicated(root):
    """N epochs, in months, computed — never typed.

    The claim never expires (socaity-ipg clause 3); after N epochs it hardens
    to the adjudication path.  N and the epoch length are both published
    parameters, so the human-time figure on the page is derived from them at
    render, per the visual standard's "every number is derivable".
    """
    if root not in sys.path:
        sys.path.insert(0, root)
    from ledger.validator import DEFAULT_V
    from rule.params import PLACEHOLDER_PARAMS as P

    epochs = DEFAULT_V["claim_auto_epochs"]
    days = epochs * P["L_days"]
    return {
        "epochs": epochs,
        "days": days,
        "months": round(days / 30),
        "provisional": P.get("status") != "final",
        "L_days": P["L_days"],
    }


def generate(ctx):
    env, root = ctx["env"], ctx["root"]
    horizon = _months_until_adjudicated(root)
    stamp = ctx["clock"][:10]

    with open(os.path.join(root, MERGE_COMMENT_SOURCE), encoding="utf-8") as fh:
        merge_comment = fh.read()

    # The one figure that appears in both the pasted comment and the page.
    # The comment is prose a maintainer copies into GitHub, so it cannot
    # compute anything -- but it can be held to the computed value here, which
    # is the difference between a checked number and a stale one.
    expected = ["about %s months" % form
                for form in (horizon["months"], _word(horizon["months"]))]
    if not any(form in merge_comment for form in expected):
        raise SystemExit(
            "%s must say one of %s: the horizon is computed from the published "
            "parameters (%d x %d days) and the two have drifted apart"
            % (MERGE_COMMENT_SOURCE, " or ".join(repr(e) for e in expected),
               horizon["epochs"], horizon["L_days"]))

    common = {
        "steps": STEPS,
        "verify_ssh": VERIFY_SSH,
        "verify_repo": VERIFY_REPO,
        "recompute": RECOMPUTE,
        "horizon": horizon,
        "stamp": stamp,
        "namespace": NAMESPACE,
        "login": LOGIN_PLACEHOLDER,
        "repo_blob": REPO_BLOB,
        "merge_comment_source": MERGE_COMMENT_SOURCE,
    }
    return [
        ("claim/index.html",
         env.get_template("claim.html").render(depth=1, **common)),
        ("claim/reserved/index.html",
         env.get_template("claim_reserved.html").render(depth=2, **common)),
        ("claim/merge-comment/index.html",
         env.get_template("claim_merge_comment.html").render(
             depth=2, merge_comment=merge_comment, **common)),
    ]
