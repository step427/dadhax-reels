#!/usr/bin/env python3
"""Pull like/comment counts for the account and write them up by posting time.

Nick's ask, early August: "we need to start being able to figure out ways to get
the statistics on how videos perform based on when they are posted." That ran
through Zapier until the task quota died, and nothing replaced it -- so the
publisher had been posting into the dark since ~8/12.

This runs in Actions (.github/workflows/stats.yml), which already holds the
token. It is deliberately a SEPARATE workflow from publishing: a stats failure
must never be able to take a posting slot down with it.

    python publisher/stats.py            snapshot + rewrite the report
    python publisher/stats.py --dry-run  print the report, write nothing

Two outputs, both committed back to the repo:

  stats/history.jsonl   one line per post per snapshot. Append-only, so the
                        trend is recoverable later -- a single current count
                        cannot tell you whether a reel is still gathering.
  stats/README.md       the readable cut.

Three things the first real run (8/24) taught us, all of them now handled here
because each one quietly produces a WRONG answer rather than an obvious error:

  1. The account goes back to June 2024 and carries 500+ posts. The old page
     cap of 5 stopped at exactly 500 and said nothing, so the report looked
     complete while silently dropping the tail. The cap is higher now and a
     truncated pull says so in the report.
  2. Median likes are 0 while the mean is 2.0 -- the distribution is mostly
     zeros with a handful of outliers. A mean-only table hands back "05:00 is
     a great hour, 4.8 likes" when that bucket is one viral post from Aug 2025
     carrying ten dead ones. Every table now shows n, median AND mean.
  3. Only ~52 of those posts had their hour CHOSEN by the publisher. The rest
     is two years of Nick posting by hand at whatever time he happened to be
     free. Blending them cannot answer "what hour should the machine post?",
     so the actionable tables cover the automated era and all-time is kept
     separately as context.

Insights (views, reach, watch time) need instagram_manage_insights, which this
token does not carry. Likes and comments are what is reachable.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish  # noqa: E402  -- reuse call(), creds(), log(), TZ

REPO = publish.REPO
STATS = REPO / "stats"
HISTORY = STATS / "history.jsonl"
REPORT = STATS / "README.md"
FIELDS = "id,timestamp,permalink,like_count,comments_count,media_type"
PAGE_CAP = 30          # 3000 posts; the account had ~500 on 8/24
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_media(ig, tok, pages=PAGE_CAP):
    """Every post the account can see, newest first, following the cursor.

    Returns (posts, truncated). `truncated` is the thing that matters: hitting
    the cap silently is how a partial pull gets read as a complete one.
    """
    out, after = [], None
    for _ in range(pages):
        params = {"fields": FIELDS, "limit": 100, "access_token": tok}
        if after:
            params["after"] = after
        page = publish.call("GET", f"{ig}/media", params)
        out.extend(page.get("data", []))
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if not after or not page.get("data"):
            return out, False
    return out, True


def central(ts):
    """Graph hands back '2026-08-21T14:50:12+0000'. Nick thinks in Central."""
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(publish.TZ)


def kinds_by_permalink():
    """fresh vs back-catalog, read off the queue rather than guessed.

    Doubles as the era marker: a permalink the queue knows about is a post the
    publisher made, so it is the only kind whose HOUR the machine chose.
    """
    try:
        q = json.loads((REPO / "queue.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {i["permalink"]: ("back-catalog" if publish.is_old(i) else "fresh")
            for i in q.get("items", []) if i.get("permalink")}


def already_snapshotted(today):
    """Has today's snapshot already been written?

    Guards the backup run below from double-counting. Cheap tail read rather
    than parsing the whole file: today's rows, if any, are at the end.
    """
    if not HISTORY.exists():
        return False
    tail = HISTORY.read_text(encoding="utf-8").splitlines()[-800:]
    return any(f'"snapshot": "{today}"' in line for line in tail)


def snapshot(media, today):
    """Append today's counts. One line per post, so nothing is ever overwritten."""
    STATS.mkdir(exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as fh:
        for m in media:
            fh.write(json.dumps({
                "snapshot": today,
                "id": m["id"],
                "posted": m.get("timestamp"),
                "likes": m.get("like_count", 0),
                "comments": m.get("comments_count", 0),
            }, sort_keys=True) + "\n")


def _table(rows, headers):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _stat_row(label, likes):
    """n, median, mean, best -- in that order, because median is the honest one."""
    return (label, len(likes), f"{statistics.median(likes):.1f}",
            f"{statistics.mean(likes):.1f}", max(likes))


STAT_COLS = ["Posts", "Median", "Mean", "Best"]


def _grouped(posts, key):
    g = defaultdict(list)
    for p in posts:
        g[key(p)].append(p["likes"])
    return g


def _by_hour(posts):
    g = _grouped(posts, lambda p: p["when"].hour)
    return [_stat_row(f"{h:02d}:00", v) for h, v in sorted(g.items())]


def _by_dow(posts):
    g = _grouped(posts, lambda p: p["when"].strftime("%a"))
    return [_stat_row(d, g[d]) for d in DOW if g[d]]


def report(media, today, truncated=False):
    kinds = kinds_by_permalink()
    posts = []
    for m in media:
        if not m.get("timestamp"):
            continue
        posts.append({
            "when": central(m["timestamp"]),
            "likes": m.get("like_count", 0),
            "comments": m.get("comments_count", 0),
            "permalink": m.get("permalink", ""),
            "kind": kinds.get(m.get("permalink", ""), "hand-posted"),
        })
    posts.sort(key=lambda p: p["when"], reverse=True)
    auto = [p for p in posts if p["kind"] != "hand-posted"]

    lines = ["# @nicksdadhax — likes and comments by posting time", "",
             f"Snapshot {today}. {len(posts)} posts, {len(auto)} of them posted "
             "by the publisher. Generated by `publisher/stats.py`; do not "
             "hand-edit.", ""]
    if truncated:
        lines += ["> **Partial pull.** The page cap was reached, so the oldest "
                  "posts are missing from this snapshot. Raise `PAGE_CAP`.", ""]
    lines += ["Likes and comments only — views and reach need "
              "`instagram_manage_insights`, which this token does not carry.",
              "",
              "**Read the median, not the mean.** Across the whole account the "
              "mean is a few likes and the median is zero: most posts get "
              "nothing and a handful go off. One old viral post can make a "
              "dead hour look like the best hour on the board.", ""]

    if auto:
        first = min(p["when"] for p in auto).strftime("%Y-%m-%d")
        lines += [f"## The automated era ({len(auto)} posts since {first})", "",
                  "The only posts whose hour the publisher actually chose — so "
                  "the only ones that can answer what the machine should do "
                  "next.", "",
                  "### By hour posted (Central)", "",
                  _table(_by_hour(auto), ["Hour"] + STAT_COLS), "",
                  "### By weekday", "",
                  _table(_by_dow(auto), ["Day"] + STAT_COLS), "",
                  "### Fresh vs back-catalog", ""]
        g = _grouped(auto, lambda p: p["kind"])
        lines += [_table([_stat_row(k, v) for k, v in sorted(g.items())],
                         ["Kind"] + STAT_COLS), ""]

        # Hour and kind are ENTANGLED here: the 1pm slot is the repost slot, so
        # every back-catalog reel is also a 1pm reel. Reading either table on
        # its own gets the driver backwards -- it did on 8/24, where the kind
        # table alone said content type was doing the work and this cross-tab
        # said the hour was. Neither is settled; the cell that would settle it
        # is fresh-at-1pm, which has never been posted.
        lines += ["### Hour x kind — which one is actually driving it", "",
                  _table([_stat_row(f"{k} @ {h}", v) for (k, h), v in sorted(
                      _grouped(auto, lambda p: (p["kind"],
                                                f"{p['when'].hour:02d}:00")).items())],
                         ["Bucket"] + STAT_COLS),
                  "",
                  "An empty cell is not a zero — it is an experiment nobody has "
                  "run yet.", ""]

    lines += [f"## All time, for context ({len(posts)} posts)", "",
              "Mostly Nick posting by hand at whatever hour he was free, going "
              "back to 2024. Useful as history, not as a scheduling signal.", "",
              _table(_by_hour(posts), ["Hour"] + STAT_COLS), "",
              _table(_by_dow(posts), ["Day"] + STAT_COLS), ""]

    top = sorted(posts, key=lambda p: p["likes"], reverse=True)[:10]
    lines += ["## Top 10 by likes", "",
              _table([(p["when"].strftime("%Y-%m-%d %H:%M"), p["likes"],
                       p["comments"], p["kind"], p["permalink"]) for p in top],
                     ["Posted (CT)", "Likes", "Comments", "Kind", "Link"]), ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the report, write nothing")
    args = ap.parse_args()

    c = publish.creds()
    if not c["META_ACCESS_TOKEN"] or not c["IG_USER_ID"]:
        sys.exit("missing IG_USER_ID / META_ACCESS_TOKEN")
    # the error body can echo the query string back, token included
    publish._REDACT = [c["META_ACCESS_TOKEN"], c["META_PAGE_TOKEN"]]

    media, truncated = fetch_media(c["IG_USER_ID"], c["META_ACCESS_TOKEN"])
    publish.log(f"pulled {len(media)} posts{' (TRUNCATED)' if truncated else ''}")
    today = datetime.now(publish.TZ).strftime("%Y-%m-%d")
    text = report(media, today, truncated)

    if args.dry_run:
        print(text)
        return
    if already_snapshotted(today):
        # The backup cron caught a day the primary already covered. Refresh the
        # readable report, but never append a second set of rows for one day --
        # that would double-weight it in any trend read off history.jsonl.
        REPORT.write_text(text, encoding="utf-8")
        publish.log(f"{today} already snapshotted - report refreshed, history untouched")
        return
    snapshot(media, today)
    STATS.mkdir(exist_ok=True)
    REPORT.write_text(text, encoding="utf-8")
    publish.log(f"wrote {REPORT.relative_to(REPO)} and appended to history")


if __name__ == "__main__":
    main()
