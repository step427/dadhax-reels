#!/usr/bin/env python3
"""Engagement sliced by CRAFT, not by clock.

    python publisher/craft_report.py        write stats/CRAFT.md

Why this exists (2026-08-31). stats.py answers "what HOUR should the machine
post?" -- hour, weekday, fresh-vs-catalog. Every one of those is a SCHEDULING
question. Nothing in the pipeline ever asked "did this EDIT work?", so 67KB of
craft rules in SAM-PLAYBOOK.md had never been checked against Nick's own
audience -- the playbook studies Sam Gaudet's numbers, this studies Nick's.

It joins two files nobody had joined:
  queue.json            what we DID to a reel (topic_class, kind, cover, collab)
  stats/history.jsonl   what the audience DID back
on `permalink`, which stats.py started recording the same day this was written.

RETENTION is the point. avg_watch_time / duration = the share of the reel people
actually sat through, and it is the only number that says whether a hook held.
Likes are a weak proxy on a small account (median ~2).
"""
import json
import statistics
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish  # noqa: E402

REPO = publish.REPO
STATS = REPO / "stats"
HISTORY = STATS / "history.jsonl"
QUEUE = REPO / "queue.json"
REPORT = STATS / "CRAFT.md"

# verified live 2026-08-31; `plays` is NOT a valid metric on this edge
METRICS = ("views,reach,saved,total_interactions,"
           "ig_reels_avg_watch_time,ig_reels_video_view_total_time")


def latest_by_permalink():
    out = {}
    if not HISTORY.exists():
        return out
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        pl = r.get("permalink")
        if not pl:
            continue          # rows written before 2026-08-31 carry no permalink
        prev = out.get(pl)
        if prev is None or r.get("snapshot", "") >= prev.get("snapshot", ""):
            out[pl] = r
    return out


def queue_posted():
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    items = q if isinstance(q, list) else q.get("items", q.get("queue", []))
    return [i for i in items if i.get("status") == "posted" and i.get("permalink")]


# posted cuts are moved out of the repo once they ship; this is where they land
ARCHIVE = Path.home() / "Rook" / "_tools" / "reels" / "archive-posted"
# measured durations, keyed by permalink. Kept OUT of queue.json on purpose:
# GitHub Actions commits queue.json back, so a local write there races the cloud.
DURCACHE = STATS / "durations.json"


def _probe(src, timeout):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(src)],
            capture_output=True, text=True, timeout=timeout)
        return float(r.stdout.strip())
    except Exception:
        return None


def duration_s(fname, mid, tok, cache):
    """Seconds of finished cut, from whichever source still has the file.

    Local file -> Instagram's own copy -> cache. 80 of the first 91 posted cuts
    no longer exist on disk (they ship, then get cleared), which is why the
    duration column read `unknown` for 67 of 76 reels and retention -- the whole
    point of this report -- survived on n=9. Instagram still hosts every one of
    them, and ffprobe reads `format=duration` straight off the CDN URL without
    downloading the file. Measured once, cached forever: a reel's length never
    changes, so this costs one Graph call per reel per lifetime.
    """
    f = fname and next((c for c in (REPO / fname, ARCHIVE / fname) if c.exists()), None)
    if f is not None:
        return _probe(f, 30)
    if mid in cache:                      # None caches too: a miss stays a miss
        return cache[mid]
    d = None
    try:
        url = publish.call("GET", mid, {"fields": "media_url",
                                        "access_token": tok}).get("media_url")
        if url:
            d = _probe(url, 120)
    except Exception:
        return None                       # transient -- do NOT cache the failure
    cache[mid] = d
    return d


def insights(mid, tok):
    url = f"https://graph.facebook.com/v21.0/{mid}/insights?metric={METRICS}&access_token={tok}"
    try:
        d = json.load(urllib.request.urlopen(url, timeout=30))
        return {x["name"]: x["values"][0]["value"] for x in d.get("data", [])}, ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        if "instagram_manage_insights" in body:
            return {}, "token lacks instagram_manage_insights"
        return {}, f"HTTP {e.code}"
    except Exception as e:
        return {}, type(e).__name__


def dur_bucket(s):
    if s is None:
        return "unknown"
    for hi, lab in ((20, "under 20s"), (35, "20-35s"), (50, "35-50s"), (70, "50-70s")):
        if s < hi:
            return lab
    return "over 70s"


def table(groups, label, pct=False):
    rows = []
    for k in sorted(groups, key=lambda k: -statistics.median(groups[k])):
        v = groups[k]
        f = (lambda x: f"{x:.0f}%") if pct else (lambda x: f"{x:.1f}")
        rows.append((k, len(v), f(statistics.median(v)), f(statistics.mean(v)), f(max(v))))
    if not rows:
        return [f"_No data for {label}._", ""]
    out = [f"| {label} | n | median | mean | best |", "|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out + [""]


def main():
    hist = latest_by_permalink()
    tok = publish.creds()["META_ACCESS_TOKEN"]
    joined, why = [], ""
    cache = json.loads(DURCACHE.read_text(encoding="utf-8")) if DURCACHE.exists() else {}
    cache_at_start = dict(cache)

    for p in queue_posted():
        h = hist.get(p["permalink"])
        if not h:
            continue
        dur = duration_s(p.get("file"), h["id"], tok, cache)
        rec = {
            "topic": p.get("topic_class") or "unclassified",
            # publish.is_old() reads the kind off the filename prefix and has
            # since 8/15. Reading p["kind"] instead -- a field only 6 of 91 rows
            # ever carry -- is why this column was 71/76 `unknown`.
            "kind": "back-catalog" if publish.is_old(p) else "fresh",
            "collab": "collab" if p.get("collaborators") else "solo",
            "cover": "custom cover" if p.get("cover_ms") is not None else "default cover",
            "len": dur_bucket(dur),
            "likes": h.get("likes", 0),
        }
        ins, err = insights(h["id"], tok)
        why = why or err
        rec.update(ins)
        awt = ins.get("ig_reels_avg_watch_time")
        if awt and dur:
            rec["retention"] = min(100.0, (awt / 1000.0) / dur * 100.0)
        joined.append(rec)

    L = ["# Craft report - engagement by how the reel was CUT", "",
         f"Joined **{len(joined)}** posted reels (queue.json x history.jsonl on permalink).", ""]

    if not joined:
        L += ["**Nothing joined yet.** history.jsonl only began recording `permalink` "
              "on 2026-08-31, so this fills in from the next `stats.py` snapshot "
              "onward. Re-run after tonight's snapshot.", ""]
    if why:
        L += [f"> **Insights unavailable:** {why}.", ""]

    dims = (("topic", "topic"), ("len", "duration"), ("kind", "fresh/catalog"),
            ("cover", "cover"), ("collab", "collab"))

    if any("retention" in j for j in joined):
        L += ["## Retention - the edit-quality metric", "",
              "_Share of the reel actually watched. This is the hook test._", ""]
        for d, lab in dims:
            g = defaultdict(list)
            for j in joined:
                if "retention" in j:
                    g[j[d]].append(j["retention"])
            L += table(g, lab, pct=True)

    for key, lab in (("views", "views"), ("reach", "reach"),
                     ("saved", "saves"), ("likes", "likes")):
        if not any(key in j for j in joined):
            continue
        L += [f"## By {lab}", ""]
        for d, dlab in dims:
            g = defaultdict(list)
            for j in joined:
                if key in j:
                    g[j[d]].append(j[key])
            L += table(g, dlab)

    L += ["---", "",
          "**Read the median, not the mean** - one outlier makes a dead format look alive.", "",
          "**An empty cell is not a zero** - it is a cut nobody has tried yet.", ""]

    STATS.mkdir(exist_ok=True)
    if cache != cache_at_start:
        DURCACHE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    REPORT.write_text(chr(10).join(L), encoding="utf-8")
    publish.log(f"wrote {REPORT.relative_to(REPO)} ({len(joined)} reels joined)")
    if why:
        publish.log(f"NOTE: {why}")


if __name__ == "__main__":
    main()
