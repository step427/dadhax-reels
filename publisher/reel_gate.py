#!/usr/bin/env python3
"""The reel gate: four fields every queue row must carry before it posts.

Prose rules fail. The index-row rule was missed 4x in its first week, and Sam is
skipped on routine cuts, so most reels never had a recorded verdict at all
(BUILD-QUEUE #24, Nick 9/14: "how do we ensure this happens for every editing
process, every week, every tool"). Only code at the point of no return holds,
and the publisher is that point -- it runs on GitHub with no session.

    arc_slot      which slot on the week's arc sheet this reel fills
                  (Rook/_tools/reels/arcs/ARC-current.md)
    pix           P | I | X -- proven / iteration / experiment (70/20/10,
                  SAM-PLAYBOOK "story layer" section)
    value_forms   exactly 2 of entertainment / idea / implementation
    sam_verdict   "POST YYYY-MM-DD" -- a recorded director verdict

ROLLOUT: WARN-ONLY. publish.py --status prints a count and posts regardless,
same rollout as the topic-mix check. Flipping the publisher to skip-and-report
is a separate, deliberate change (ENFORCE below), not a date that trips on its
own -- a gate that silently empties the queue breaks three-a-day, which is the
one thing that does not get traded.

    python publisher/reel_gate.py                       every pending row
    python publisher/reel_gate.py --file ig-0914-x.mp4  one row (queue_insert, the loop)
    python publisher/reel_gate.py --arc PATH            also check the arc sheet's age

Exit 1 when anything fails, so a local step can gate on it. Stdlib only.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ENFORCE = False          # flip only on purpose; publish.py stays warn-only until then
ARC_MAX_AGE_DAYS = 8
PIX = {"P", "I", "X"}
VALUE_FORMS = {"entertainment", "idea", "implementation"}
VERDICT = re.compile(r"^POST (\d{4}-\d{2}-\d{2})$")
REQUIRED = ("arc_slot", "pix", "value_forms", "sam_verdict")
QUEUE = Path(__file__).resolve().parent.parent / "queue.json"
ARC = Path.home() / "Rook" / "_tools" / "reels" / "arcs" / "ARC-current.md"


def check_row(row):
    """Return a list of failures for one queue row; empty means it passes."""
    fails = []
    slot = row.get("arc_slot")
    if not isinstance(slot, str) or not slot.strip():
        fails.append("arc_slot missing")
    if row.get("pix") not in PIX:
        fails.append("pix missing" if "pix" not in row else f"pix {row['pix']!r} not P/I/X")
    vf = row.get("value_forms")
    if vf is None:
        fails.append("value_forms missing")
    elif (not isinstance(vf, list) or len(vf) != 2 or len(set(vf)) != 2
          or not set(vf) <= VALUE_FORMS):
        fails.append(f"value_forms {vf!r} not 2 of {sorted(VALUE_FORMS)}")
    verdict = row.get("sam_verdict")
    if verdict is None:
        fails.append("sam_verdict missing")
    else:
        m = VERDICT.match(str(verdict).strip())
        if not m:
            fails.append(f"sam_verdict {verdict!r} not 'POST YYYY-MM-DD'")
        else:
            try:
                date.fromisoformat(m.group(1))
            except ValueError:
                fails.append(f"sam_verdict date {m.group(1)!r} invalid")
    return fails


def arc_age(path=ARC, today=None):
    """Days since the arc sheet was written, or None if there is no sheet.

    Reads the first ISO date in the file (the sheet's `updated:` line) rather
    than mtime: OneDrive/Drive sync touches mtime without anyone planning a week.
    A sheet with no date at all counts as missing -- an undated plan is not a plan.
    """
    path = Path(path)
    if not path.is_file():
        return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", path.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    try:
        written = date.fromisoformat(m.group(0))
    except ValueError:
        return None
    return ((today or date.today()) - written).days


def summary(rows):
    """(passing, total, {failure-kind: count}) for the --status line."""
    kinds = {}
    ok = 0
    for r in rows:
        f = check_row(r)
        ok += not f
        for x in f:
            k = x.split(" ")[0]
            kinds[k] = kinds.get(k, 0) + 1
    return ok, len(rows), kinds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default=str(QUEUE))
    ap.add_argument("--file", help="check one row by its file name")
    ap.add_argument("--arc", nargs="?", const=str(ARC),
                    help="also check the arc sheet is <= %d days old" % ARC_MAX_AGE_DAYS)
    a = ap.parse_args()

    items = json.loads(Path(a.queue).read_text(encoding="utf-8"))["items"]
    if a.file:
        rows = [i for i in items if i.get("file") == a.file]
        if not rows:
            print(f"FAIL {a.file}: not in {a.queue}")
            return 1
    else:
        rows = [i for i in items if i.get("status") == "pending"]

    bad = 0
    for r in rows:
        f = check_row(r)
        if f:
            bad += 1
            print(f"FAIL {r['file']}: " + "; ".join(f))
        else:
            print(f"ok   {r['file']}")
    if a.arc:
        age = arc_age(a.arc)
        if age is None:
            bad += 1
            print(f"FAIL arc sheet: missing or undated at {a.arc}")
        elif age > ARC_MAX_AGE_DAYS:
            bad += 1
            print(f"FAIL arc sheet: {age} days old (max {ARC_MAX_AGE_DAYS}) -- plan the week")
        else:
            print(f"ok   arc sheet: {age} days old")
    print(f"{len(rows) - sum(1 for r in rows if check_row(r))} of {len(rows)} rows pass"
          + ("" if ENFORCE else "  [WARN-ONLY: the publisher still posts every row]"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
