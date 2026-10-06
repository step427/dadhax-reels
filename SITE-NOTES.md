# Site structure & why — step427.github.io/dadhax-reels

Built 2026-08-08. Read this before redesigning anything; every choice here is a
decision with a reason, not a default.

## The thesis: the reader is the hero, Nick is the guide

Nick asked "from a zoomed out perspective, how do these connect?" and answered it
himself — *"it's my life that's the connection."* That's right for the **reels**
and wrong for the **site**, and the difference is the whole design.

StoryBrand's central finding is that brands lose when they cast themselves as the
hero. The structure that works is: a character (the reader) has a problem, meets a
**guide** (who has walked it), gets a plan, and is called to act. On this site
Nick's life is not the subject — **it is the credential that qualifies him to
guide.** Hence the About section is titled "Who's writing these," is four short
paragraphs, and ends on *"You're the one doing the work here. I'm just the guy a
little further up the same road, yelling back about where the potholes are."*

The site's promise is Nick's own line, barely edited: **you don't have to pay what
I paid.** Headline "None of this is secret — it's just scattered" comes straight
from his "the information is already free, I'm just compiling it" framing. That is
the guide promise and it is honest, which is why it works.

## Navigation: visible, not a hamburger

Nick's first instinct was a hamburger. The research says no, and it isn't close.

NN/g, 179 participants across 6 sites, phone and desktop: hidden navigation cut
discoverability by **~20%**; visible nav was found and used **1.5× as often** on
mobile; desktop users missed hidden nav **almost 2× as often**; task completion was
**39% slower on desktop, 15% slower on mobile**.

Hamburgers are for hierarchies too deep to show. **Three sheets is not that.**
The 2026 pattern that holds up is 3–5 visible items plus overflow behind a tap —
never everything behind the tap.

**Revisit at sheet 8–10.** At one a week that is roughly October. The move then is
grouping (topic hubs), not hiding — keep the 3–5 strongest visible and let the
overflow collapse.

Nav links are `min-height:44px`. A nav link too small to hit forfeits the entire
argument for visible nav.

## The real gap was never a menu

Before this, every sheet ended with one link back to the index. **Every sheet was a
dead end.** Someone finished the AI sheet — the one promised on camera — and their
only move was backwards to a list.

Each sheet now ends in the sequence Nick specified: **value first, then the ask.**

    next sheet  →  sign up  →  DM / follow / share

`Read next` is a real recommendation, not a shuffle: 01 → 02 → 03 → 04 → 01. Find
the why, how wiring changes, what to do about it, then how to sort the ideas the
doing generates — and back to the why.

## The signup, and the promise it nearly broke

"No signup, no email — nothing here to collect" appeared **13 times across 4 pages**
and in live Instagram captions. Adding a form naively breaks Nick's word in public
on the exact trait he sells.

**The line that resolves it, and it makes the offer stronger:** the *sheets* ask
for nothing — no gate, no wall, no email to read a word. The list is the **only**
thing on the site that asks for anything, and it is opt-in. The contrast is now the
argument: everyone else gates the content and begs for the email; this site gives
the content away and mentions the list once.

Sheet copy changed from *"no signup"* to *"no gate"* and *"this sheet asks you for
nothing."* Still true, still checkable.

⚠️ **"You'll have a say in what I build next" is only true if Nick actually asks.**
If the list collects emails and never asks a question, it is a lie by the standard
this whole operation is held to. **The first email has to ask one.** That is a
commitment, not a flourish.

## The signup ships in two stages — `optin.py`

The account did not exist when the site shipped (both Buttondown endpoints 404'd,
checked, not assumed). A form POSTing to nothing gives every reader an error page,
on a site whose whole pitch is "no catch." So the slot ships **designed and honest**
and activates in one command:

```
python _tools/reels/optin.py --check     # is the account live yet?
python _tools/reels/optin.py --pending   # DM-first block, no form  (current)
python _tools/reels/optin.py --live      # real subscribe form
```

`--live` **refuses to run** while the endpoint is dead (override with `--force`, and
don't). It edits all four pages together so they can never disagree.

The pending copy says the true thing — *"the list isn't open yet, I'm still building
it, and I'd rather say that than put up a box that doesn't work"* — and routes to the
DM, which Nick's own content playbook calls the money step anyway. Admitting the seam
costs nothing here; it is on-brand for a site selling "no catch."

## Form endpoint

    https://buttondown.email/api/emails/embed-subscribe/nicksdadhax

Written against the handle Nick already owns everywhere, so it goes live the moment
the account exists — no code change. **If he registers a different username, that
string in `index.html` and in the three sheets is the only edit.**

Chose an email tool over a form-to-spreadsheet because *sending* is the promise —
"first to hear" is worthless if there is no way to send.

## The Toolbox (renamed from "The Tools", 2026-08-14)

Nick's call: the nav button IS a toolbox. Each nav chip carries a small inline
SVG toolbox whose lid pops open on hover/focus (`.tbx` in site.css — `.toolbox`
was already taken by the tool pages' tail link). On index, the `#tools` heading
has the same icon and the lid swings open when the section scrolls into view
(tiny IntersectionObserver at the bottom of index.html — no network, no storage,
the privacy copy stays true). That scroll-open is the mobile show, since phones
don't hover. The SVG carries `fill`/`stroke` presentation attributes so it
renders correctly standalone; outwit-the-devil.html doesn't link site.css and
carries its own copy of the icon CSS in its style block.

## Files

- `site.css` — shared chrome only (nav, tail, optin, CTA row). Every page keeps its
  own `<style>` and its own `:root` (dark-only: log.html's light-mode flip was removed
  10/05 after it turned the page white in previews and on light phones). Additive on
  purpose: one copy of the shared parts instead of four that drift.
- `index.html` — landing page **and** catalog. It is a homepage, correctly: multiple
  visitor intents. The single-CTA discipline applies to the optin block, not the page.
- `queue-b7f3a91c.html` — private reel queue board. noindex, never linked from index.

## The story spine (Nick's direction, 2026-08-10)

Every weekly tool ties to **the theme he's posting on that week** — the tool is a
chapter, not a random drop. Storytelling is the frame because that's how people
actually learn and attach: each tool page carries (1) a bit of the running story and
(2) a short first-person "why this one was useful for me" beat, told in story mode.
Tool 04 got its beat retroactively: the notes-app confession — years of a brain-dump
list, and the only year-over-year difference was *a longer list*.

Two mechanics every tool should end on, added to 04 and standard going forward:
- **The boulder question.** "Most problems aren't about what you know — who you
  know. Name one person you can call who'd push the boulder even the smallest way.
  Now make the call." The call is the universal next-best-action.
- **The AI prompt.** If the tool can't compute a personalized output itself, it
  hands the user a copyable, quality-framed prompt for whatever AI they already use
  — plus, where possible, a loop/automation to keep pursuing it.

## Tool 05 brief — Why Your Side Gig Wants an LLC

The story (Nick's, told once-upon-a-time style): a good boy followed the path his
folks and the generations before him prescribed, without question, and excelled at
nearly every stop on it. Then one day he's got his own family, gray hairs coming in,
and a sense of a life not yet lived nagging at him. A calling to take control of his
own path — no idea where to begin. So he took the next best step that inspired him
(prescribed, oddly, by yet another authority figure — but one he *chose*, because
they lived a version of the life he wanted). Without yet knowing what value he'd
give the world, he opened his first LLC.

Who it's for: the dad with the gnawing gut feeling and the weight on his shoulders
saying he's capable of more. The tool's job is to turn "someday" (i.e. never) into
this year, this month, this day.

The deliverable when someone finishes: (1) an LLC actually set up, and (2) a north
star / framework built on their *own* current skills and asymmetric advantage —
network, skills, whatever they already hold. If the page can't customize that
output, it hands them the AI prompt that will, plus a loop or automation to pursue
in relation to it. Boulder question + call at the end, per the spine.

⚠️ Honesty rails for 05: no legal or tax advice — plain-language "why a container
helps," and "ask your accountant/attorney" where it counts. Same no-gate promise.

## The relaunch — page-per-job architecture (Nick's call, 2026-08-15)

Nick: "there's legitimately just too much going on on the home page… each page
needs its own specialty and focus." And the refocused vision, his words distilled:
**the brand promise is "make the life of a Dad more POWERFUL," not easier.** Two
lanes: make the trivial easy (bag→bowl, claw-hammer carries the plywood — new
perspective on ordinary things buys back time) so you can spend it on the hard
work that matters — dad, husband, productive member of society, impact in your
direct community. The site is a framework toward a purpose-filled life.

The map (research-backed: StoryBrand section order, NN/g one-job-per-page,
single-CTA evidence — full report in agent transcripts 8/15):

- **index.html — orientation & story ONLY.** Hero (kept) → the turn
  (easier→powerful) → two lanes → guide block → 3-step plan → ONE CTA (the
  Toolbox door, lid animates) → "New this week" line → optin #next (optin.py
  still targets it — do not rename the anchor) → footer (view-source trust line,
  houses one-liner). Old #tools/#houses hashes JS-redirect to the new pages.
- **toolbox.html — pick a tool.** Owns the #tools identity, lid opens on
  arrival, cards newest-first, sealed 06 card. ⚠ TUESDAY FLIP now happens HERE
  (the sealed card moved off index — flip instructions in the toolbox.html
  comment still apply, plus remove outwit's gate block + robots meta).
- **houses.html — the seller offer, alone.** Full pitch moved verbatim from
  index. Nav keeps its "I have a house" chip (kept against strict research
  advice — it's the money channel; deliberate call).
- **log.html — proof of cadence.** Unchanged content, nav made consistent.
- Tool pages unchanged except nav/tail links → toolbox.html / houses.html.
  Their .buyhouses tail sections stay (8/9 audit: deep-link traffic never sees
  the homepage).

GitHub scan verdict (8/15): in-house workflow beats available skills; worth
adapting someday: anti-slop design checklist (jiji262/claude-design-skill),
axe-core pass bolted onto audit.js.

**Tail change, supersedes the 8/8 "DM / follow / share" trio:** the three-button
IG row at the bottom of every tool page is gone (critique loop 8/15: five
buttons to one URL was the only funnel-smelling spot on the site). The tail
sequence survives with less noise — next sheet → optin block (share ask + one
DM button). "Tell me in the comments" phrasing became "DM me" — no comments
exist on-site. Tool pages mark the Toolbox chip aria-current="true" (inside
the section), real pages use "page"; site.css matches bare [aria-current].

## The yellow grammar (Nick flagged "color scheme is off," 8/15 relaunch night)

Signal yellow #FFC629 has exactly three jobs, in this order, and the relaunch
briefly broke them by using yellow as a voice instead of a scalpel:
1. **SOLID yellow block = the one primary action on the page.** The gate button,
   the optin button, the Toolbox door. ONE per page, never two.
2. **Thin yellow = small mono labels and marks.** Section tags, sheet numbers,
   "open the tool," lane tags, plan numbers, one left-border.
3. **Yellow prose = at most one bold phrase per zone** (the thesis line, the
   optin ask). Never whole link-sentences, never bold link rows, never the
   footer as a yellow wall.
If a screen shows more than one loud yellow element, the hierarchy is broken —
strip until the primary action is unmistakable.

## Story-first is law (Nick, 2026-08-15)

Storytelling is the skeleton of everything this operation makes — the site, each
tool, every post. Humans move on story, not information. Every new artifact gets
a story pass before it ships: who's the hero (always the reader), what's the
negative force, what instrument do they leave with. The site-wide frame is the
hero's journey with the reader early in theirs; Nick is the guide, never the hero.

## Tool 06 — the Devil's character law + chapter frame (story pass 2026-08-15)

**The character law (Nick's rule):** the Devil names every concept by its NEGATIVE
form — he is the negative forces personified, so a virtue never appears in his
mouth under its positive name. Impatience, never eagerness. Drift, never rest.
Stubbornness, never persistence. The bribe, never comfort. Borrowed opinions,
never education. His flattery is bait; his endearments ("friend") are
condescension; his honesty arrives only when literally cornered, grudging or
tolled. He NEVER praises, encourages, coaches, or uses hero-language about the
player — a dare is the closest he comes. His one fear (definite purpose + a plan
in motion) is always framed as "a problem I have no tool for," never admiration.
Only THE TABLE (narrator, clinical mono) and the site-owner voice (story note,
attribution) may frame the player hero-positively.

**The chapter frame:** this tool is one early chapter of a hero's journey — the
first close look at the antagonist (vast, bored, certain, doesn't rate you yet)
combined with the first real fight, which is against a PHANTOM wearing his
costume, not the man himself. Winning it is real skill; the copy is the only
reason the fight is winnable tonight. The hero leaves with the enemy's whole
playbook and one instrument: the well-aimed open question. The win line is the
emotional spine — no praise from him, just distaste at what the player is
becoming, echoing the 7th confession's "now forget I said it." (Private
structural reference: young hero's first courtyard exchange + the phantom
duel — never named in page copy.)

## Tool 06 — clunk pass (drifter-persona audit, 2026-08-15)

Nick called the tool clunky and story-thin; a full journey audit (home page →
gate → game → closer, run in persona: a drifter on the verge of discovery,
10:40pm, phone) agreed. The fixes, and why they stay:

- **The gate is a hint ladder and a door, not a wall.** Misses hand over more of
  the answer; the third miss opens the door anyway with a sneer and brands the
  session a drifter (his opener changes). A lockout in front of the best content
  was the #1 reader-loss point. Body scroll locks while the door is shut.
- **Lines arrive on beats.** say() renders through a queue — the devil pauses
  ~750ms behind a "…" while he considers you; the table follows a half-step
  behind. Instant replies read as a vending machine, not a presence.
- **The devil's first line is personal.** He names the thing you keep "thinking
  over" before you ask anything — the one moment the fiction reaches through the
  glass, moved from a random mid-game bait to the opener.
- **Truth costs him.** Every confession pays +20s back (capped at 5:00), so
  reading his best paragraphs is never punished by his own clock.
- **Voice is muted by default** and even opted-in he only speaks lines ≤14 words
  — the browser robot reading an 80-word confession broke the fiction.
- **CRAFT % lives only in the debrief.** A live percentage is a rubric; he
  scores you, the table doesn't.
- **Preamble collapsed** to one "Before you sit" block (Start ~1.7 screens from
  top, was 2.4); the owner's origin note moved below the game, by the credit.
- **The closer is staged.** Only the open-question field shows until it's
  answered; then the decision + "text them tonight" (a 10:55pm dad can send a
  text; he cannot make a call).

## Gate

Every page audited at 375px with `_tools/web/audit.js` before it ships: **PASS,
zero warnings**, including tool 04 (2026-08-10) audited in its fully-expanded state.
Nothing ships without re-running it.

**Calibration note (2026-08-11, tool 05 ship):** the LONG/DENSE warnings now fire
on *every* tool page in fully-expanded state because the standard tail (~250 words)
plus the story beat grew the fixed overhead — re-measured, shipped tool 04 itself
reads 981 words / 5491px expanded. So the working gate is: **zero FAILs, zero
fixable warnings (squashed/overflow/tiny/contrast/tap/links), and density at or
near 04 parity.** Tool 05 shipped at 995 words / 5965px expanded — and ~60 of
those words are the audit's own test input + the generated north star. If a future
page beats 04's density meaningfully, tighten this note.

Tool 05 (side-gig-llc.html) shipped 2026-08-11: audit PASS, zero fails, density
at 04 parity. Chain is now 01→02→03→04→05→01. Index carries a titleless "06 — in
the shop" card (next week's tool comes from next week's story; no false promise).

## Publishing runs on GitHub Actions (2026-08-12)

`.github/workflows/publish.yml` fires `publisher/publish.py` at 14:00 / 18:00 /
23:00 UTC — 9am / 1pm / 6pm Central while CDT is in effect. It takes the next
eligible item out of `queue.json`, posts it to Instagram and the Facebook page,
marks it posted, prunes the mp4, and commits the queue back.

**Why it moved:** it used to be a Windows Scheduled Task on Nick's laptop. A
laptop that is asleep can be woken; a laptop that is off cannot. That produced a
zero-post day on 8/7 and two missed slots on 8/12.

**Required repo secrets** (Settings -> Secrets and variables -> Actions):
`IG_USER_ID`, `META_ACCESS_TOKEN`, `META_PAGE_TOKEN`. Values live only in
`Rook/_local-secrets/meta-ig.env` on Nick's machine — never in this repo.

**Never add a `pull_request_target` trigger.** This repo is public. Secrets are
withheld from fork pull requests, which is what keeps schedule + manual dispatch
safe; `pull_request_target` would hand them to arbitrary PR code.

`queue.json` here is the single source of truth. The reel loop pulls, appends
new cuts, and pushes. Both publishers commit their result so neither re-posts
what the other already put out.

## Tool 06 went public (2026-08-18)

`outwit-the-devil.html` — the interrogation game — lost its field-test gate on
schedule (scheduled flip, Nick in the Boundary Waters): riddle door, three-try
lock, and `noindex` all removed; nav meta now "free · no gate". The toolbox's
sealed devil card became a normal open card and an 07 "in the shop" placeholder
took its slot. Read-next chain now runs 05 -> 06 -> 02 (the rhythm confession
hands off to neuroplasticity on purpose — same machinery, pointed the other way).
The unused `a.card.devil` styles stay in toolbox.html for the next sealed-door
pre-launch — the teaser pattern is worth repeating.

## Tool 09 — The Cabinet Run (built 2026-09-05 as 08, renumbered 09 on 2026-09-14; the flip is Nick's)

`cabinet-run.html`. Born the same day out of the mudroom build: a 93 3/4" wall, a
9-ft ceiling, an AI chat that invented a "window nook" off two numbers on a sketch,
and a rendering that looked finished. The tape closed it — 1 7/8 + 30 + 30 + 30 +
1 7/8 = 93 3/4, 90 + 18 = 108 — and then the house brand turned out not to make
that pantry in 30 wide. The tool does the part that saved the project: wall +
ceiling (+ optional window) in, every stock-width composition that closes within
3" of slack out, ranked (uniform widths first, then symmetric, fewest boxes, least
slack), plus tall+upper stacks that land within 4" of the ceiling, the window
flagged into its bay, and the search strings for the desk. Two rails: the 24-inch
trap, and "confirm the tall width exists FIRST." Same privacy contract
(sessionStorage, no network). Story beat is first-person, honest; closers are the
boulder question and an AI-review prompt that forbids invented products/prices.

Engine notes: compositions are ordered (so 24+36+30 and 30+36+24 both appear —
that's intentional, a window can sit in either); a pick that turns "bad" after the
window is entered re-picks the top row; `frac()` renders sixteenths. One real bug
shipped and was caught in the audit pass: a self-referencing gcd closure that threw
on any non-integer — if the page ever shows 0 runs for a sane wall, look there.

Gate (2026-09-05, 375px, fully expanded with the mudroom numbers): **PASS, zero
fails**, 1080 words / 6067px expanded — 05 parity (995 / 5965). Lists capped at 3
rows each to get there; the first draft was 1795 / 8195 and failed TOO LONG.

Chain: 07 → **08** → 04 (the rendering was Fantasy until the tape made it
Testable). Toolbox card 08 live, 09 "in the shop"; index "New this week" points at
08; 07's titleblock reads 07 of 08. Branch `tool-08-cabinet-run`, not pushed —
Nick merges/pushes Tuesday after his own look.

**Renumbered to Tool 09 (2026-09-14).** The Decision Forcer shipped as 08 on 9/08
while this sat on its local branch. Rebased onto main as `tool-09-cabinet-run`:
chain is now 07 → 08 Decision Forcer → **09 Cabinet Run** → 04 (08's tail used to
loop to 02). Toolbox card 09 live, 10 "in the shop", index reads "Nine free tools"
and "New this week" points at 09, and the titleblocks read 07/08/09 of 09. The
branch-only notes above are kept as history.

## The four-beat open (Nick's direction, 2026-09-19) — and the check that enforces it

Nick, looking at Tool 09: *"you don't have a very good intro that describes what the
tool is doing for a person, and why it's useful... it's pointless to create tools that
nobody uses, and nobody will use a tool if they don't understand what it's for."*

He was right, and the uncomfortable part is that **the doctrine for this was already
on this page.** "The reader is the hero, Nick is the guide" has been the thesis since
August: *a character has a problem, meets a guide, gets a plan, and is called to act.*
Tool 09 shipped opening with an aphorism, then a definition of the mechanism, then
Nick's own story — the reader's problem never stated, and Nick's life promoted from
**credential** to **subject**, which is the exact inversion the thesis warns about.

So this is not new doctrine. It is the old doctrine given an **order** and a **meter**.

### The order — all four, before the first input

1. **PROBLEM** — their situation, in their words. A pain they already have, not one
   the page has to teach them to feel first.
2. **PRICE** — what it costs to keep guessing. Stakes, and why now.
3. **PROMISE** — the artifact they walk out holding. A thing, never an adjective.
4. **PROOF** — it working on real numbers, *before* anything is asked of them. The
   council's own Value Architect lens already demanded this: *does the page look like
   it works in the first five seconds? Bought with proof and a visible mechanism,
   never with adjectives.*

Then the two rules that were already standard: the first input costs under ten
seconds, and the answer leaves the page (the boulder question, the AI prompt, a
copyable output).

**The mechanism definition is beat five, not beat one.** "Stock cabinets come in a
handful of widths. A wall comes in one" is a good line. It just cannot be the first
thing a stranger reads, because it explains a thing they have not yet agreed to care
about.

### The meter — `_tools/web/intro_audit.py`

```
python3 _tools/web/intro_audit.py --live        # all live tools
python3 _tools/web/intro_audit.py page.html
python3 _tools/web/intro_audit.py --selftest
```

It measures the mechanical shadow of the four beats: how much framing exists before
the first input, whether the opening addresses a reader at all, second-person density
across the intro, and whether a concrete number appears before the ask. It cannot
judge whether the problem named is the *right* one — that judgment stays with the
Sunday routine, exactly as `council.py` leaves scoring to Claude.

**First run, 2026-09-19, ranked by second-person density:**

| Page | density | note |
|---|---|---|
| 7-layers-of-why | 0.092 | the benchmark |
| outwit-the-devil | 0.061 | |
| start-with-ai | 0.053 | but 972 words before the tool — a wall |
| side-gig-llc | 0.050 | |
| decision-forcer | 0.049 | no proof number |
| stop-block | 0.043 | no proof number |
| fact-testable-fantasy | 0.036 | |
| neuroplasticity | 0.033 | 550 words — a wall |
| **cabinet-run** | **0.023** | **worst on the site**, and its only "you"s were in the privacy notice |

Tool 09 was measurably the least reader-addressed page of the nine — a quarter of Tool
01's rate. Nick caught that by eye. After the rewrite: **0.038, clean pass.**

### The check was wrong first, and got tuned — not skipped

Its first version counted the nav as opening copy, so every page "opened" with
*@nicksdadhax Tool 09 free no gate Home The Toolbox The Log* — twenty words of
furniture that masked the exact defect it was built to find. It scored Tool 09 a PASS.
Chrome is now stripped before anything is measured.

Same rule `audit.js` and `aeo_audit.py` both live under: **when a check misses the real
one, fix the check and write down why.** Skipping its output is what is not allowed.

### Still owed on the older pages

`start-with-ai` (972 words) and `neuroplasticity` (550) bury their tools under walls of
intro. Tools 06, 07 and 08 carry no concrete number before the ask. None of these are
FAILs; all of them are the retrofit queue.

## Tool 10 — The Cleat Wall (built 2026-09-22 by `dadhax-weekly-tool`, ships Tue 9/29)

`cleat-wall.html`. Council pick 9/22 (83.9; runner-up Past Fine 75.9, banked). The
implementation layer of `ARC-2026-09-20` ("the wall does the storing", easter egg **45**).
Wall width in (everything else defaults: rails 16→80 every 8, studs 16 o.c., first stud
at 16, 4" strips); out comes rails + heights, 45° rips, sheets, stud marks, screws, rail
pieces split so **every joint lands on a stud**, and hanger/stop counts. Engine is a
pure `plan()` function; pieces pack first-fit-decreasing into 96" strips with a 1/8"
kerf. The dek's proof line (10-ft wall → 9 rails, 12 rips, 2 sheets, 144 screws) was
computed by that engine; if the engine changes, re-run it and fix the sentence.

Story beat is Nick's own words only: `ig-0908-cleat101` caption (90% of the garage, no
shed), `ig-0912-cleathub` (office nook three years ago → backpack hub), `ig-yt-stop`
(hangers fell off until the stop), cleat long-form yt:y9Z-vIpuY38 ("rip a 45 … whole
garage in a weekend"), and his Gemini chat "Plywood Tool Holder Demo" (the AI drew the
cleat backwards and forgot the mirroring piece). Rails: screws into studs only, "this page
doesn't know your wall." Boulder question carries last week's "third thing".

**Launch reel (S7 path 1):** repost `ig-0908-cleat101.mp4` "This is why I don't need a
shed" (source_raw `20260907_120012.mp4`) under a catalog prefix, caption rewritten so the
45 pays off and the one link is `https://step427.github.io/dadhax-reels/cleat-wall.html`.

**Rip math corrected 2026-09-30 (hotfix; Nick caught it off his own saw setup).** The 9/22
engine split every strip "down the middle" into one wall half + one hanger half, gave no
fence number, and defaulted to a 4" strip (~2 5/16" cleats, not the 3" Nick builds and
films). Now: the input is **finished cleat height** (default 3, id `height`, replaces
`strip`); fence = height − 3/4; strip = 2·fence + 3/4 + 3/16 (a 1/8 kerf at 45° eats 3/16
across the face) → **5 7/16 strip, fence 2 1/4**; one pass makes **two wall cleats**, so
strips = half the 96" cleat lengths. Hangers are their own stock: 1 3/4" cleats from a
2 15/16 strip (fence 1), 5" plates, 3/4" stops, 8" per hanger, all counted in the sheets.
Rail heights now print as **bottom edge**. Gap warning fires under height + 2. The proof
line above is now **9 rails, 6 rips, 1 sheet, 144 screws** (2 sheets with 30 hangers); the
9/29 launch caption and its `log.html` copy still say "twelve rips, 2 sheets" and are left
as the record of what was posted. Engine checked against Rook `captures/_tools/cleat_cutlist.py`.
`silva` review 9/30: FIX, applied (saw-safety line `oSaw`, orientation sentence in the dek,
cleat height clamped 1.75 to 3.25 because the 5" plate's stop lands on a taller rail, spacing
warning under max(height + 2, 6), "construction screws, not drywall"). Left for Nick: screw
gauge and plywood grade (silva wants cabinet-grade named). Not done here (next Sunday build): the "behind a workbench?" 6"/12" toggle and the spacer line.

**Zones + videos (2026-09-30, Nick: "pre-fill the numbers recommended by my experience ... the PT background should be highlighted").** One switch, "Is this wall behind a workbench?": Yes = rails every 6 from 40 to 88 (the default, and the dek's proof line: 9 rails, 6 rips, 1 sheet for the rails, 144 screws); No = every 12 from 16 to 88. The switch clears typed rail numbers so it visibly wins. Spacing is Nick's; the 40 and 16 start heights are placeholders until he gives his own. A fourth why-item carries the PT reasoning in his words (wellness lane: his wall, his reasoning, no clinical claim). A second story panel LINKS the wall tour (yt:y9Z-vIpuY38), `ig-diy-cleatwall` and `ig-0912-cleathub` on Instagram and Facebook (`facebook.com/reel/<fb_page_video_id>`). Links only, never embeds: the page promises no outside calls. The "One 45, two cleats" why-item was cut to stay under the TOO LONG line (now 8.3 screens; the next addition has to remove something).

**Output is numbered steps with a picture each (2026-09-30, Nick: "add a little image of the cuts at the associated step ... bullets and steps help us humans stay on task").** The cut list is seven `.step` blocks (Buy, Rip the strips, Cut the 45, Cut the rails, Mark the studs, Screw on the rails, Build the hangers), each a 72px inline SVG + mono heading + short bullets; saw warnings are `li.w` with a red "!" marker. Built in `refresh()` from one `steps` array that "Copy the cut list" also reads, so the two cannot drift. Steps are `div`s, not `ol > li`: the audit counts an outer `li`'s words and FAILed it as a wall (83), and a picture beside the bullets SQUASHED them to 175px, so the picture sits in the heading row. The orientation paragraph in the dek was cut; step 6's picture carries it. 8.4 screens.

**Paired strips (2026-09-30, Nick's idea).** One strip now yields a wall cleat on the fence side and a hanger cleat as the offcut: width = wall cleat's short face + 45° kerf + hanger cleat's wide face = 2 1/4 + 3/16 + 1 3/4 = **4 3/16** (Nick's first sum, 4 15/16, added both wide faces and counted the 3/4 bevel run twice). `pairStrips = min(hanger lengths, wall cleat lengths)`; leftover wall cleats come two-per 5 7/16 strip; the 2 15/16 / fence 1 strip survives only when hangers outnumber rails. The fence stays at 2 1/4 for every bevel cut. 10-ft bench wall + 30 hangers: 3 at 4 3/16 + 5 at 5 7/16, still 2 sheets, 13 wall cleats (1 spare) + 3 hanger cleats. `silva` 9/30: FIX, applied (scrap test measures the OFFCUT and corrects the strip width, never the fence; "leave the offcut until the blade stops"; the nerves line sits after the hard checks, not instead of them). Silva rates the safety gain as modest (more push-shoe room, one setting) and found no named source for "wider piece against the fence", so the page does not print that as a rule. Assumes true 3/4 stock and a 1/8 blade. 8.5 screens: at the limit.

**Rail profile is Nick's three zones (2026-09-30, second correction).** Inputs are now lowest rail (18, his), bench top (36, a placeholder he has not confirmed) and ceiling (96); "Highest rail" and "Rail spacing" are gone. Rails step 12 below the bench and above 108, 6 from the bench to 108; the top rail's bottom edge stops at ceiling − 3 − 1. "No workbench" = 12 all the way. 10-ft wall, 8-ft ceiling: 11 rails (18, 30, 42 … 90), 8 rips, 1 sheet, 176 screws = the dek's proof line. Spacer blocks print as gap − 3 (3 or 9); "start at the bottom, work up" and the glue + brad-nail line are his pro tips. Cut the "Studs, not drywall" why-item to stay under TOO LONG (the steps and the red note carry it). 8.5 screens.

**Audit fills (Tool 10):** `--fill wall=120 bottom=18 bench=36 ceiling=96 oc=16 first=16 height=3 hang=30 callName=Sam` — every input the page needs set before its real output exists on screen. Never a real person's name or a sensitive number.
→ PASS, 984 words / 5636px expanded (09 is 1170 / 6557). The `.redline-note` background
is the solid composite `#20130E` instead of `rgba(232,80,44,.08)` because the audit
reads the translucent one as 1:1 contrast; same look. `decision-forcer.html` still
carries that pre-existing CONTRAST warn (not touched beyond its titleblock).

Chain: 09 → **10** → 04. Toolbox card 10 live, 11 "in the shop", index "Ten free tools"
+ "New this week" → 10, titleblocks 07/08/09/10 read "of 10" (01–05 still read "of 05",
as they did at the 09 ship).

## The Log's headliner video (2026-10-05, Nick's call)

Nick: *"why aren't we having this be the headliner video? It summarizes pretty much
the whole journey pretty quick."* The reel is "too far gone" (IG `Dbl-A5EBSXa`,
posted 8/3, the reel loop's `out-flipdone-v5`). It now sits under the "One old house"
h1 in `log.html`, ahead of the eight-part arc: the short version first, the long one
below for whoever wants it.

- **Self-hosted, not embedded.** Instagram's `/embed` is dead (8/9), and a native
  `<video preload="none">` makes no outside call until the reader taps play, so the
  site's "nothing here watches you read it" promise holds. `one-old-house.mp4`
  (H.264 720x1280, faststart, ~9MB) + `one-old-house.jpg` poster sit at the root.
  **Never add `one-old-house.mp4` to `queue.json`.** The publisher's prune deletes
  any file whose queue rows are all `posted`.
- **This is the clean cut, not the IG upload.** The live IG version still carries
  the street address three ways: spoken + burned-in karaoke at 0:00-2.6, the porch
  number plate through ~4.7s, and the number beside the red door in the closing
  shot. This was flagged 8/4 and never reposted. The house has an occupant. The web cut
  starts at 3.55s on "Get this flip done", blurs the strip above the hook bar
  through the porch shot (the hook bar is punched back in sharp), and runs a tracked
  blur on the door number from 39.44s on. Gated on the render at full res, every
  frame of both windows, plus a Whisper transcript (the address is spoken only at
  0.00-2.56).
- **log.html is generated.** `Rook/_tools/reels/build_log.py` rewrites it 3x a day,
  so the same block has to live in the builder or the next rebuild wipes it. The
  patch is in Rook `captures/` (2026-10-05).

## The Flip — One Old House story page (live 2026-10-05)

The nav label "The Log" became **"The Flip"** on 14 pages; the URL stays `log.html`.
`build_log.py` now carries the story: `STORY_LIVE = True` (the 3x-daily rebuild
regenerates it), `--draft DIR` renders a preview that never pushes, and chapter clips
are `file:NAME.mp4|label` entries that play on click and render only if the mp4 sits
beside the page. All four chapter clips + the headliner are self-hosted (YouTube
embeds can't load inside a claude.ai artifact preview, and they make an outside call).
Every clip passed the address gate on the render (frames, audio, captions). Nothing
from the contractor dispute goes on this page. Already-published videos stay up (Nick,
10/05); the gate applies to new cuts. Clip recipe: Rook CAPABILITY-INDEX, site-clip row.

## Tool 11 — The Sheet Plan (built 2026-10-04 by `dadhax-weekly-tool`, ships Tue 10/6)

`sheet-cut-plan.html`. Council pick 10/02 (71.1; runner-up Past Fine 67.2, banked), re-scoped
to a one-day build. The implementation layer of `ARC-2026-10-04` ("the second trip to the
store", easter egg **an eighth**). Parts list in (one per line or `;`-separated: qty, length x
width, optional name; fractions like `34 1/2` parse; the longer side is taken as length, with
the 8-ft grain), sheet size and kerf default to 96 x 48 and 1/8. Engine is rip-first: group
parts by width, first-fit-decreasing each width's lengths into full-length strips (kerf between
pieces), then FFD the strip widths across sheets. A near-miss pass trims one width by up to
1/2" and reports it only if that saves a whole sheet. Output is four `.step` blocks (Buy, Rip,
Crosscut, Mark) built the same way as Tool 10's. The textarea is prefilled with the example on
first load so output exists before a keystroke (the Value Architect's design-against).

The dek's proof line (shelf unit, 72 tall x 16 deep, five shelves + a kick → 3 sheets; 15 7/8
deep → 2) was computed by the engine; if the engine changes, re-run it and fix the sentence.
The red rail is "this page doesn't nest parts" and names cutlistoptimizer.com, the free tool
Nick's own reels recommend (give-first means pointing at the better tool).

Story beat is Nick's own words only: `ig-diy-cutlist` ("I wasted a lot of plywood learning this
the other way. The free tool is better at it than I am"), `ig-yt-cutplan` (pencil and grid
paper, the stock you already have, then the cut list), `ig-0908-waste` ("every board you don't
waste is one you don't buy"), `ig-yt-sheet` (break a sheet down on the floor; "a good third
thing"). Links only, never embeds.

**Launch reel (S7 path 1):** re-cut posted `ig-yt-cutplan.mp4` "Plan the cuts before you buy
wood" (source_raw `yt:c7Wh-xcTYhA`) under a catalog prefix, the way cleatwall re-cut cleat101,
with the shelf-unit numbers in the caption and the one link
`https://step427.github.io/dadhax-reels/sheet-cut-plan.html`. This is the council's test of
the deep link on a non-cleat theme (falsifier in `BRIEF-2026-10-02.md`).

**Audit fills (Tool 11):** `--fill "parts=2 sides 72 x 16; 5 shelves 34 1/2 x 16; 1 kick 34 1/2 x 3 1/2" sheetL=96 sheetW=48 kerf=0.125 callName=Sam` — every input the page needs set before its real output exists on screen. Never a real person's name or a sensitive number.
→ PASS WITH WARNINGS (LONG/DENSE only), 1013 words / 5781px expanded, Tool 10 parity
(984 / 5636). `intro_audit.py` PASS, 381 words before the ask, you-density 0.047.

Chain: 10 → **11** → 04. Toolbox card 11 live, 12 "in the shop", index "Eleven free tools" +
"New this week" → 11, titleblocks 07–11 read "of 11" (01–06 unchanged, as at the 10 ship).

## Tool 11 v1.1 — cut drawings + three-stage engine (built 2026-10-06, cloud session; NOT shipped)

Nick, 10/5: *"pictures are worth a thousand words... this is cut number one, two, three... in
this order because this is how we get the most out of the sheet."* Two changes, same page:

- **A drawing per sheet**, to scale, every cut a dashed line with a numbered badge. Under it is the
  numbered cut list in the same order: all the first-direction cuts, then crosscuts, then the
  small rips and trims. "At" is always measured from the fresh edge. The old text-only
  "Rip the strips" / "Crosscut the strips" steps are gone; Buy and Mark stay.
- **The engine** is three-stage: rip, crosscut, rip again. A narrow part can ride beside a wider
  one, the search tries both first-cut directions, and it keeps the fewest sheets, then the fewest
  cuts. 300 random lists: an extra sheet on 11, vs 95 for v1. Never worse than v1. 8/8 on the named
  projects, and the mudroom bench is 1 sheet. Harness: Rook `captures/_tools/sheet-plan-check/`.
- Copy changed in three places to stop describing the old engine: the "Rip first" rule box, the
  red note, and the copy/prompt assumption lines. The dek's proof line (3 sheets / 2 at 15 7/8)
  still holds and was re-checked.

**Audit (same fills as v1):** `intro_audit.py` PASS (382 words before the ask).
`audit_headless.py` PASS WITH WARNINGS (LONG/DENSE/line length only), 1120 words / 6531px.
The cut list is the added length. Record: `audits/sheet-cut-plan-a83a997a8696.json` (re-audited 10/6 after merging the shipped v1 and its nav rename, The Log -> The Flip).
**The Rook-side copy of that record is not in `Rook/_tools/web/audits/`** (cloud sessions write
only `captures/` there). The laptop must re-run `audit_headless.py` or copy the record from
here before `ship_gate.py` will pass it.
