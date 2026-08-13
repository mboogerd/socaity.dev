# Usability test protocol — M1 focus+context model (socaity-8wg)

**Status: not yet run. No results exist. `results-template.md` is empty by design.**

What is being tested: whether the focus+context interaction model (one node in
focus, breadcrumbs up, ranked lists down, no free-form canvas) lets a developer
navigate a >50-node ingested-issue graph, contest an edge, and add a need —
and whether they correctly predict what happens when an OR branch loses.

What is **not** being tested: visual design, copy polish, the ingestion quality
of the decomposer, or whether people want the platform. Say this out loud to
participants; it changes what they report.

Artifact: `prototype.html` — open it in any browser, no server, no network.
Seed graph: 52 nodes / 53 edges of `vectorlite/vectorlite` (fictional repo,
realistic ingested-issue shape), schema-shaped per `council/socaity-sbb.md`,
weights bucketed per `council/socaity-6kb.md`. The >50-node threshold matters:
this is the size at which product-designer's prior says a free-form canvas
fails, so the graph must exceed it for the test to mean anything.

---

## 1. Recruitment

**N = 5.** Five is enough to expose model-level failure; do not scale up before
fixing what five find.

Each participant must:

- ship code professionally, or maintain an OSS project, now or within 2 years;
- have used at least one issue tracker seriously (GitHub Issues, Linear, Jira);
- have a repo of their own with **more than 50 open issues** — they must have
  personally felt the backlog-too-big problem;
- not have seen the socaity graph model, vision doc, or any council file;
- not be a friend who will be kind. At least 3 of the 5 must be strangers.

Spread across: 2 solo maintainers, 2 developers on a team of 5+, 1 person who
does triage but does not primarily write code (PM, TPM, support engineer).

Exclude: anyone who has discussed this project with the founder, and anyone who
works on graph/knowledge-graph tooling (they read the model, not the UI).

Session: 45 minutes, screen-shared, recorded with consent, one facilitator.
Reward participants (money or equivalent); unpaid favours produce polite data.

## 2. Facilitator rules

- Read the framing verbatim. Improvised framing teaches the model.
- **Never say "graph", "node", "edge", "AND/OR", "OR branch", "problem node",
  "solution node" until the participant says it first.** Say "the tool", "this
  thing", "the item you are looking at". The whole hypothesis is that the model
  is legible without vocabulary.
- Silence over rescue. Count to ten before intervening.
- When asked "what should I do?" answer "what would you do if I were not here?"
- Record the first hesitation over 5 seconds and what was on screen.
- One intervention rule: if a participant is stuck >2 minutes on a task, mark
  the task **failed**, then unblock them so the session can continue. A rescued
  task is never a pass.

## 3. Framing (read verbatim)

> This is an early prototype of a triage tool. It has read the issue tracker of
> an open-source vector database called Vectorlite and reorganised it. You are
> a new maintainer on that project. I did not build this to be defended — I
> need to find out where it fails, so please think out loud, and please say
> when something is confusing or wrong. Nothing you do here can break anything.

Then: "Take one minute and tell me what you are looking at, before you click
anything." (Capture this. It is the comprehension floor from `sbb`'s gate.)

## 4. Tasks

Give one task at a time, in this order, verbatim. Start a timer per task.

### Task A — find what is blocking X

> The team has decided to go with "Harden the existing single-node engine".
> Tell me everything that has to be true before that can be called done.

- **Pass:** names all five direct requirements (one of which is flagged as a
  possible duplicate of another — noticing that is a bonus, not required), and
  at least one second-level
  requirement (for example, that the benchmark suite or the fsync problem sits
  under one of them), without being told the lists are clickable.
- **Partial:** names the five direct requirements only, or needs one prompt.
- **Fail:** misses a direct requirement, treats an alternative approach as a
  blocker, or exceeds 2 minutes.
- Record: time, path taken, whether they used breadcrumbs to get back,
  whether they ever asked for a whole-graph picture.

### Task B — dispute one edge

> Somewhere in here is a connection you think is wrong — something listed under
> something it does not really belong to. Find one and tell the tool you
> disagree.

- **Pass:** finds "Dispute this link", uses it, and their stated reason is about
  the *relationship* ("that isn't what's blocking it") rather than the node.
- **Partial:** disputes, but expected it to delete or hide the link.
- **Fail:** cannot find a way to disagree, or disputes the node believing they
  have removed it.
- Record: did they look for a delete/edit affordance first? Did they notice the
  history panel logged their name? Did they expect anyone to be notified?

### Task C — add one need

> You know something this project needs that is not in here. Add it.

- **Pass:** adds it in a place that survives the facilitator's question "why
  there?" — attached to the approach or the need it actually belongs under.
- **Partial:** adds it, but at the root or in an arbitrary spot, and cannot
  justify the placement.
- **Fail:** cannot add anything, or expects a free-text box unattached to
  anything and refuses the placement question.
- Record: did they hesitate over problem-vs-approach? Did they notice their
  addition arrived unweighted, and did that read as broken or as honest?

### Task D — the OR-branch prediction question (ask BEFORE demonstrating)

Navigate them to "Rewrite the index layer on top of Faiss". Ask, **without
touching anything**:

> Suppose the team decides against this one — they pick a different approach.
> What do you think happens to everything listed under it? Where does it go?

Capture the answer verbatim, then have them do it ("Mark this approach as
withdrawn"), then ask what surprised them.

The prototype's actual behaviour, for scoring:

1. Nothing is deleted. Node count is unchanged; the withdrawn approach stays,
   greyed, marked "withdrawn — kept for the record".
2. Requirements that **only** the losing approach needed ("There is no
   migration path…", "Faiss is a 400MB build dependency") are marked *"no live
   approach requires this"* — visible, not gone.
3. A requirement **shared** with a surviving approach ("No benchmark suite for
   recall vs latency", also required by "Prune the HNSW graph on insert") is
   untouched and still live.
4. The surviving approaches' weight chips do **not** change. No mechanism
   reprices them; the tool refuses to fake one.

Score each of the four independently as predicted / not predicted / contradicted.
Point 3 (shared vs exclusive children) is the one that matters most: it is the
difference between a graph and a tree, and if nobody predicts it, the model is
teaching a tree.

## 5. Post-task questions

1. If this were pointed at your own repo, what is the first thing you would
   look for? Would you use it? (Probe for "instead of what?")
2. Some items say "favored", "contested", "long shot", "speculative". Where do
   you think those come from, and how much would you trust them?
   - **Red flag:** any answer implying a vote, a market, a measurement, or team
     consensus. The `6kb` rule exists to prevent exactly that reading.
3. The word "unweighted" appears on some items. What does it mean to you?
4. Did you at any point want to see the whole thing at once as a map? What were
   you trying to find when you wanted it?
   - This is the focus+context hypothesis's own falsifier. Do **not** offer the
     "All nodes" button; note it only if they ask for something like it.
5. Who do you think wrote the things in here — a person or a machine? What told
   you? (Provenance chips are the designed object; test that they are read.)

## 6. Success bar (decide before running; do not move it after)

The model **passes** and the frontend may harden around it when:

- **4 of 5** pass Task A within 2 minutes with no navigational help;
- **4 of 5** pass Task B (dispute found and used unprompted);
- **4 of 5** pass Task C with a placement they can justify;
- **3 of 5** predict points 1 and 2 of the OR-branch behaviour, **and**
  **at least 2 of 5** predict point 3 (shared requirement survives), **and**
  **0 of 5** expect the tool to reprice surviving branches automatically;
- **0 of 5** describe the weight buckets as a vote, a market, a measurement, or
  team consensus (this one is absolute — a single such reading is a trust leak
  per `z61`/`6kb` and must be fixed before M1 UI work);
- **at most 1 of 5** says they needed a whole-graph map to do the tasks.

Anything short of that is a **fail of the model as prototyped**, not of the
participants. Failure means: revise the model, re-run with five new people
before any frontend work. Record which specific bar failed — the remedy for
"nobody found dispute" (an affordance fix) is nothing like the remedy for
"everybody expected deletion on withdrawal" (a model fix).

## 7. Capture

- Per session: fill one column of `results-template.md` during or immediately
  after; do not batch five sessions from memory.
- Click "Copy session log" at the end of each session and paste the log into
  the participant's row — it is the objective record of what they actually did.
- Verbatim quotes beat paraphrase, especially for Task D and question 2.
- Reload the page (or press Reset) between participants: state is in memory
  only, nothing persists, so each participant starts from an identical graph.
