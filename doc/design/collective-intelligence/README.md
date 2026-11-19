# Socaity — collective intelligence design study

Open `preview.html` to review the homepage on its own, including its styles and interactions. The editable production sources are `index.html`, `styles.css`, and `app.js`. Run `node doc/design/collective-intelligence/bundle.mjs` from the repository root to regenerate the single-file preview. Use the assembled Pages build to follow the links to the blog and research archive.

## Direction

**More than the sum of us.** An editorial, human-centred umbrella for projects that increase our capacity to understand and act together. Paper, charcoal, and a single terracotta accent; large typography; generous space; explanatory line drawings. Scale and composition carry the ambition.

The visitor moves from the societal ambition to a practical progression: start with a real need, connect useful work, let others build on it, then develop more explicit tools for collective reasoning and action. Watane is the only project presented. Future applications appear as possibilities, with no invented names, release dates, capabilities, or download links.

The interactive book-club example translates the approved direction in **Killer app concept with great UX** into a small explanatory experience: a need, a reading list and voting tool, then adaptations by other groups. Its three buttons reveal the story through a changing map and adjacent text. It is visibly labelled as an imagined journey, with no simulated agent execution, fabricated live activity, or actual publication. It introduces no second project to the directory.

The hero drawing explains how an individual contribution can be reused, adapted, and connected. Its nodes are illustrative, not claims about real participants or network activity. The drawing has a text alternative. The Watane illustration expresses a foundation that leaves room for further work.

## Architecture for growth

Each project is a self-contained semantic `article.project` inside `.project-list`. Add another sibling article with its own unique heading ID, description, status, and verified destination. The same layout supports any number of entries. Keep the single full-width feature while the ecosystem has one project; introduce an index when visitors genuinely need one.

Keep the umbrella's vision, principles, and exploratory horizon separate from project pages. Each project's own site should own installation, downloads, detailed features, and documentation. The Watane card currently uses an honest explanation disclosure in place of an unverified destination. Replace that affordance with the verified project-site link when it exists.

Native links, a native disclosure, and three keyboard-operable buttons provide the interactions. The example uses pressed states and a polite live region; without JavaScript, its complete diagram and text explanation remain visible and the buttons stay hidden. Responsive styles cover narrow mobile screens through large desktop screens; reduced-motion preference disables smooth scrolling and diagram transitions. No automatic animation or tracking is used.

## Source basis and editorial boundary

Read during this session:

- `doc/vision.md` and `doc/manifesto.md` in this repository: shared needs, self-directed participation, human judgment, openness, and shared foundations. Their earlier funding mechanism does not define this new umbrella homepage.
- `doc/standards/vocabulary-and-visual.md`: the paper-based editorial register and restraint around claims. This study introduces no financial mechanism or contribution-ledger promises.
- `/Users/merlijn/Documents/local-projects/colos/spec/VISION.md`: implicit cooperation through reusable work, followed by explicit reasoning about desires, beliefs, intentions, plans, pledges, and evidence. These are Colos's stated goals; they are not asserted as shipped Watane features.
- `/Users/merlijn/Documents/local-projects/ComputeNet/doc/spec/00-foundations/01-vision.md` and `README.md`: distributed cognition, live shared models, openness, and interest-driven participation.
- `/Users/merlijn/Documents/local-projects/Watane/spec/VISION.md` and `spec/README.md`: personal mods, agent-assisted making, work building on work, independent publication, and the explicit route arriving as applications on the substrate. Goals are described as direction, not independently verified release capabilities.
- The complete user/assistant text exchange from local Claude session `745c1e59-3b74-4894-8519-b534f4fea599`, titled **Killer app concept with great UX**: the user endorsed Wishes with a living map; a book-club example makes the needs-to-tools loop tangible. The follow-up distinguishes a prototype from working substrate functionality and leaves the statement-carrier architecture undecided. This website does not settle that architecture.
- The current user brief: socaity.dev is the broader collective intelligence umbrella, Watane is its initial bootstrap, and further applications will follow.

The previously missing sources were read on 14 November 2026 after direct folder access became available. The design now explains Watane concretely while retaining its in-development status. The umbrella foregrounds collective intelligence; it does not inherit the older site's financial mechanism as its organizing message. A verified project-site destination and installation information belong to the separate Watane site; this study makes no release or installation claims.

## Production integration

The Pages build uses this folder's editable sources for the production homepage. It combines them with the generated research archive and the blog. See [Publishing Socaity.dev](../../publishing.md) for the combined local preview and GitHub setup.

## Validation

On 14 November 2026, structural checks passed for unique IDs, accessibility references, local assets, navigation anchors, the single-project directory, and all three journey controls. JavaScript parses successfully, and the page, stylesheet, and script each returned HTTP 200 from a local preview server. Browser automation and the app preview opener were unavailable, so rendered desktop/mobile layout and live interaction behaviour still require visual review. Open `index.html` directly; no server is required.

## Sites preview

A private Sites project was registered on 14 November 2026 with project ID `appgprj_6af8255fee788191966ffaedcf10271b` and slug `socaity-collective-intelligence`. It has not been published: the supported source helper failed when Git could not resolve `git.chatgpt-team.site`. Reuse this project ID when resuming; do not register a second Site. The isolated source checkout is `/tmp/socaity-sites-WmtTZ9`, with the self-contained page at `dist/index.html` and its Sites identity in `.openai/hosting.json`. The durable design source and bundled fallback are in this folder. No credentials are stored here.
