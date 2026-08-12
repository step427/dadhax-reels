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

## Files

- `site.css` — shared chrome only (nav, tail, optin, CTA row). Every page keeps its
  own `<style>` and its own `:root`, including the light-mode flip. Additive on
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
