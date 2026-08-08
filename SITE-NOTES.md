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

`Read next` is a real recommendation, not a shuffle: 01 → 02 → 03 → 01. Find the
why, then how wiring changes, then what to do about it.

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

## Gate

All four pages audited at 375px with `_tools/web/audit.js`: **PASS, zero warnings.**
Heights 2.7 / 3.7 / 4.2 / 5.3 phone screens. Nothing ships without re-running it.
