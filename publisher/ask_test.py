#!/usr/bin/env python3
"""The keyword-ask test, run by the publisher so nobody has to remember it.

Nick's own pick on 9/24 (Elite Tactical Test): "If every utility reel closes with
'Comment TOOLS and I'll send it,' comments per utility reel go from ~0.2 to
>=0.6." It was handed to the reel-loop caption step four times (9/09, 9/24,
10/04, 10/23). It ran zero times: 163 posts went out 9/01-10/25 and not one
carried the ask. A caption habit is the one thing this pipeline can't hold,
for the same reason reel_gate exists: only code at the point of no return
holds, and the publisher is that point.

So the ask moves here. When ON, every utility reel the publisher posts is
assigned an arm, alternating:

    keyword   its closing ask is swapped for LINE (the reel's own close goes)
    control   caption untouched

and the arm is written onto the queue row as `ask_arm`, so the two halves of
the test sit side by side in the same weeks. Read it with
Rook/_tools/reels/ask_yield.py --since <the day ON was flipped>.

    python publisher/ask_test.py            selftest against every posted caption
    python publisher/ask_test.py --show F   what file F would post as, keyword arm

OFF until Nick says go, because the ask is a promise: every TOOLS comment is a
DM owed by hand (the token has no messaging scope; ManyChat's free tier hit its
25-contact cap on 10/01). triage_comments.py already routes TOOLS to its
KEYWORD lane and prints the DM to paste. Flip ON and nothing else changes.

Stdlib only. A bug in here must never cost a post: publish.py calls apply()
inside a try and posts the original caption if it raises.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ON = False      # Nick's "go" flips this. False = the publisher never touches a caption.
KEYWORD = "TOOLS"   # the only keyword triage_comments.py matches -- keep them in step
LINE = ("Comment TOOLS and I'll DM you every free tool I've built. "
        "No email, no signup.")

QUEUE = Path(__file__).resolve().parent.parent / "queue.json"
SIGN_OFF = re.compile(r"^\s*Thanks, Dad\b", re.I)
FOOTER = re.compile(r"^\s*Free tools:", re.I)
CURRENT_FOOTER = "Free tools: step427.github.io/dadhax-reels"
# Every ask the reel loop's captions use, as sentences: the follow-reason close,
# the 10/06 SAVE + SEND how-to close, "show this to ...", and the bio / YouTube
# pointers. The bio and YouTube patterns are caption_gate.py's (Rook/_tools/reels)
# so ask_yield.py scores the keyword arm as ONE ask, not TWO-ASKS. Keep in step.
ASKS = [
    re.compile(r"^\s*(follow|send this|show this|save this|share this|tag (a|the|your))\b", re.I),
    re.compile(r"\bfollow (so|for|before|if|along|to)\b|\bfollow[.!]?\s*$", re.I),
    re.compile(r"\b(link|links|it'?s|list) (is )?in (my|the) (bio|profile)\b", re.I),
    re.compile(r"\b(full|whole|rest of the|entire)\b[^.\n]{0,60}\b(video|breakdown|build|walkthrough|system)\b"
               r"[^.\n]{0,80}\byoutube\b", re.I),
]
HAS_KEYWORD = re.compile(r"\bcomment\s+[\"“']?[A-Za-z]+[\"”']?\s+(and|&|to|below|for)\b", re.I)


def with_keyword(caption):
    """The caption with its asks swapped for LINE, which goes right above the sign-off.

    One variable: the ask. Only the last three paragraphs above the sign-off are
    touched, and only whole sentences that ask for something; the rest stays word
    for word ("Full walkthroughs like this one. Follow so you don't miss them."
    keeps its first sentence).
    """
    paras = caption.split("\n\n")
    at = next((n for n, p in enumerate(paras) if SIGN_OFF.match(p)), None)
    if at is None:
        at = next((n for n, p in enumerate(paras) if FOOTER.match(p)), len(paras))
    for n in range(max(1, at - 3), at):
        sentences = re.split(r"(?<=[.!?])\s+", paras[n].strip())
        paras[n] = " ".join(s for s in sentences if not any(a.search(s) for a in ASKS))
    # The August footer "Free tools — full list in my profile." is itself a bio
    # ask; the current footer is a plain address.
    paras = [CURRENT_FOOTER if n > at and p.lstrip().startswith("Free tools") and ASKS[2].search(p)
             else p for n, p in enumerate(paras)]
    paras.insert(at, LINE)
    return "\n\n".join(p for p in paras if p.strip())


def next_arm(items):
    """keyword or control: the opposite of the last posted utility reel that carried an arm."""
    armed = [i for i in items if i.get("status") == "posted" and i.get("ask_arm")]
    armed.sort(key=lambda i: str(i.get("posted_at", "")))
    return "control" if armed and armed[-1]["ask_arm"] == "keyword" else "keyword"


def apply(item, items, topic_class, log=print):
    """Assign this utility reel an arm and rewrite its caption for the keyword arm. Idempotent."""
    if not ON or topic_class(item) != "utility":
        return
    if item.get("ask_arm"):
        return  # a retried post keeps the arm it was given
    if HAS_KEYWORD.search(item["caption"]):
        item["ask_arm"] = "keyword"  # written by hand: counts, untouched
        return
    arm = next_arm(items)
    if arm == "keyword":
        item["caption"] = with_keyword(item["caption"])
    item["ask_arm"] = arm
    log(f"ASK TEST {item['file']}: {arm} arm")


def selftest():
    q = json.loads(QUEUE.read_text(encoding="utf-8"))["items"]
    caps = [i["caption"] for i in q if i.get("caption")]
    bad = []
    for cap in caps:
        out = with_keyword(cap)
        if out.count(LINE) != 1 or not HAS_KEYWORD.search(out):
            bad.append(("no single ask line", cap[:60]))
        elif any(SIGN_OFF.match(p) for p in cap.split("\n\n")) and \
                not any(SIGN_OFF.match(p) for p in out.split("\n\n")):
            bad.append(("lost the sign-off", cap[:60]))
        elif len(out) > 2200:
            bad.append(("over IG's 2,200-char cap", cap[:60]))
        elif with_keyword(out).count(LINE) > 2:
            bad.append(("runaway on reapply", cap[:60]))
    # alternation + idempotence, offline
    global ON
    was, ON = ON, True
    tc = lambda i: i.get("topic_class", "utility")
    rows = [{"file": f"t{n}.mp4", "status": "pending", "topic_class": "utility",
             "caption": "Hey Dad,\n\nDo the thing.\n\nFollow so you don't miss it.\n\nThanks, Dad. I love you, Dad."}
            for n in range(4)]
    arms = []
    for n, r in enumerate(rows):
        apply(r, rows, tc, log=lambda m: None)
        apply(r, rows, tc, log=lambda m: None)  # retry: must not flip or double the line
        r.update(status="posted", posted_at=f"2026-10-2{n}")
        arms.append(r["ask_arm"])
    talk = {"file": "x.mp4", "status": "pending", "topic_class": "talk", "caption": "Hey"}
    apply(talk, rows, tc, log=lambda m: None)
    ON = was
    if arms != ["keyword", "control", "keyword", "control"]:
        bad.append(("arms do not alternate", str(arms)))
    if rows[0]["caption"].count(LINE) != 1 or "Follow" in rows[0]["caption"]:
        bad.append(("keyword arm did not swap the close", rows[0]["caption"]))
    if LINE in rows[1]["caption"] or "ask_arm" in talk:
        bad.append(("control or talk reel was touched", ""))
    for why, what in bad:
        print(f"FAIL {why}: {what!r}")
    print(f"{len(caps) - len(bad)} of {len(caps)} queue captions transform cleanly; "
          f"arms {arms}; ON={ON}")
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", metavar="FILE", help="print FILE's caption as the keyword arm would post it")
    a = ap.parse_args()
    if a.show:
        q = json.loads(QUEUE.read_text(encoding="utf-8"))["items"]
        item = next((i for i in q if i["file"] == a.show), None)
        if not item:
            sys.exit(f"{a.show} is not in queue.json")
        print(with_keyword(item["caption"]))
        return
    sys.exit(0 if selftest() else 1)


if __name__ == "__main__":
    main()
