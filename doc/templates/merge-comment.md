# The merge comment

This is the comment a maintainer posts when a contribution is accepted. It is
checked in, and it is rendered on the site at `/claim/merge-comment/`, because
the claim invitation is the single highest-stakes piece of copy in the M0
contribution path (council/socaity-ipg.md, clause 3) and it must not be
improvised once per pull request.

**It is a template, not a form letter.** The first line is written fresh every
time and names what actually changed, in the maintainer's own words. Everything
after it is fixed copy and should be pasted unedited — every sentence in it is
load-bearing against something: a deadline that does not exist, a valuation the
claim does not change, a name nobody may publish without being asked.

## Rules that come with it

1. **Post it at merge, not after the entry is written.** The merge is the
   moment of belonging and it waits on nothing.
2. **Never add urgency.** No scarcity phrasing, no counts, no "first N", no
   deadline, no timer, nothing that implies the invitation could run out. If
   the copy below ever starts to feel like it needs a nudge, the answer is a
   better page, not a nudge.
3. **Ask before naming them anywhere else.** The record names a key. Naming a
   person in a post, a digest or a release note needs that person's yes, asked
   for in plain words, with "no" as a complete answer.
4. **If the claim never comes, that is fine and it is not a failure.** One
   friendly follow-up after a week or so, and then nothing. The contribution
   stands, the entry stands, the invitation stays open.
5. **Fill both placeholders.** `<WHAT CHANGED>` and `<PERMALINK>`. A merge
   comment posted with a placeholder still in it is worse than no comment.

## The template

```
Merged — thank you. <WHAT CHANGED, IN PLAIN WORDS, ONE OR TWO SENTENCES: what
this fixes or adds, and what it means for someone using the project.>

An entry for it is already on the record, dated to the week the work happened
and valued by the published rule. It does not name anyone yet: it reads
"attribution reserved", and it is bound to the author of this pull request —
you.

<PERMALINK TO THE ENTRY>

Attaching it to a key only you hold takes three commands and a minute or two:
https://socaity.dev/claim/

Your entry never expires. There is no deadline and nothing to be early for;
after about six months, claiming it takes one extra verification step, and
that is the only thing that ever changes.

If you would rather not, that is a complete answer. The change is merged, it
stays merged, and the git history says it was yours either way. And if I ever
want to mention this work anywhere beyond the record itself, I will ask you
first.
```

## What the maintainer does next

Write the acceptance entry with the contributor field empty and the binding set
to the SHA-256 of `github:<the pull request author's login>`, **with the login
folded to lower case** — a GitHub login is case-insensitive, the contributor
types their own at step 2 in whatever case they please, and a binding computed
from a different case is a binding that will never match:

```
printf 'github:%s' <THEIR-LOGIN> | tr 'A-Z' 'a-z' | shasum -a 256
```

That binding is what makes the invitation true, and it can only be fixed now,
before anyone knows whether the claim will come.

When the contributor posts their attestation, verify it before recording
anything — save the comment to a file, or paste it on stdin:

```
python3 tools/claim/verify_claim.py --login <THEIR-LOGIN> pasted-comment.txt
```

Check by eye the one thing the script cannot: that the comment really was
posted by that account. Then reply with the permalink, in a sentence, with no
ceremony attached to it beyond thanks.
