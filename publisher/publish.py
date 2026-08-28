#!/usr/bin/env python3
"""Post the next queued reel to Instagram, then to the Facebook page.

This runs on GitHub Actions (.github/workflows/publish.yml), and that is the
entire point of it existing. The old publisher was a Windows Scheduled Task on
Nick's laptop; a closed lid meant a silent zero-post day (8/7, and again 8/12
with two missed slots). WakeToRun cannot power on a machine that is off, so no
Task Scheduler setting could have fixed it. GitHub's schedule does not care
whether his laptop is open.

    python publisher/publish.py            post the next eligible item
    python publisher/publish.py --status   print the queue, post nothing
    python publisher/publish.py --dry-run  everything except the publish call
    python publisher/publish.py --prune    delete posted mp4s from the checkout

Credentials come from the environment (GitHub Secrets: IG_USER_ID,
META_ACCESS_TOKEN, META_PAGE_TOKEN), falling back to Nick's local
_local-secrets/meta-ig.env so the same script still runs by hand on the laptop.
Nothing secret is ever written to disk or to the log.

queue.json in this repo is the single source of truth. The reel loop appends to
it (pull, append, push); this script consumes it and commits the result back.

The day's MIX is 2 fresh cuts to 1 reformatted back-catalog reel (Nick, 8/15,
after a day of three straight reposts). Queue order no longer decides that on
its own -- see claim_next.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
QUEUE = REPO / "queue.json"
RAW_BASE = "https://raw.githubusercontent.com/step427/dadhax-reels/main/"
GRAPH = "https://graph.facebook.com/v21.0"
FB_PAGE_ID = "1146254621914259"          # Nicksdadhax page — public id, not a secret
LOCAL_ENV = Path.home() / "Rook" / "_local-secrets" / "meta-ig.env"
POSTS_PER_DAY = 3                        # the contract. Slots are just delivery.
CATCHUP_GAP = 120                        # seconds between two posts in one run

# Reformatted back-catalog: the old YouTube cuts (ig-yt-) and the DIY hacks
# (ig-diy-). Everything else is a fresh shoot.
OLD_PREFIXES = ("ig-yt-", "ig-diy-")
OLD_PER_DAY = 1                          # 2 fresh : 1 reformat (Nick, 2026-08-15)
FRESH_PER_DAY = POSTS_PER_DAY - OLD_PER_DAY


def is_old(item):
    """Reformatted back-catalog, or a fresh shoot?

    ponytail: read the kind off the filename prefix instead of adding a field to
    every one of the 40-odd queue rows. The reel loop already names files this
    way, so nothing has to be migrated and nothing new has to be remembered. An
    explicit "kind": "new" | "old" in queue.json wins if it is ever set.
    """
    return item.get("kind", "old" if item["file"].startswith(OLD_PREFIXES)
                    else "new") == "old"


def _central():
    """Slots are Nick's local time, not UTC.

    Windows ships no tz database, so zoneinfo raises there and the laptop
    fallback path would die on import. A fixed -5 is close enough: the only
    thing the timezone decides is which DATE an `earliest` check falls on, and
    every slot (9am / 1pm / 6pm) sits nowhere near midnight in either CST or CDT.
    """
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("America/Chicago")
    except Exception:
        return timezone(timedelta(hours=-5), "CT")


TZ = _central()


def log(msg):
    print(f"{datetime.now(TZ):%Y-%m-%d %H:%M:%S}  {msg}", flush=True)


def creds():
    """Environment first (Actions), local env file second (laptop by hand)."""
    out = {k: os.environ.get(k, "") for k in
           ("IG_USER_ID", "META_ACCESS_TOKEN", "META_PAGE_TOKEN")}
    if not out["META_ACCESS_TOKEN"] and LOCAL_ENV.exists():
        for line in LOCAL_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out.setdefault(k.strip(), "")
                if k.strip() in out and not out[k.strip()]:
                    out[k.strip()] = v.strip().strip('"')
    missing = [k for k in ("IG_USER_ID", "META_ACCESS_TOKEN") if not out.get(k)]
    if missing:
        sys.exit(f"missing credentials: {', '.join(missing)} "
                 "(set them as GitHub Secrets, or run on the laptop with "
                 "_local-secrets/meta-ig.env in place)")
    return out


# Meta returns a 500 with "is_transient": true and tells you, in the payload, to
# retry later -- their documented behaviour for error code 2. This used to take
# that at face value and drop the slot: 8/21 lost the 1:00p reel to exactly this
# and 8/17 lost 9:00a. The day still reached three posts, because the next run
# tops the day up, but it got there by posting two reels two minutes apart --
# worse for reach than the slot it was covering for.
_RETRY_STATUS = (500, 502, 503, 504)
_RETRIES = 4
_BACKOFF = 5  # seconds, doubling: 5, 10, 20


def _scrub(body):
    """The error body can echo the query string back, token included."""
    for secret in _REDACT:
        if secret:
            body = body.replace(secret, "<redacted>")
    return body


def _is_transient(status, body):
    if status in _RETRY_STATUS:
        return True
    try:
        err = json.loads(body).get("error", {})
    except ValueError:
        return False  # truncated or non-JSON body; the status is all we have
    return bool(err.get("is_transient")) or err.get("code") == 2


def call(method, path, params, retry=True):
    """POST/GET the Graph API, retrying what Meta flags as transient.

    `retry=False` is for calls that must not be repeated blind. media_publish is
    the one that matters: if it succeeded server-side but the response was lost,
    a retry posts the reel twice. Letting that one fail is cheap -- the item
    stays pending and the next run builds a fresh container for it.
    """
    data = urllib.parse.urlencode(params).encode()
    for attempt in range(_RETRIES if retry else 1):
        if method == "GET":
            req = urllib.request.Request(f"{GRAPH}/{path}?{data.decode()}")
        else:
            req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raw = e.read().decode()[:400]
            transient = _is_transient(e.code, raw)
            err = RuntimeError(f"Graph API error {e.code} on {path}: {_scrub(raw)}")
        except urllib.error.URLError as e:
            transient = True
            err = RuntimeError(f"network error on {path}: {e.reason}")

        if not transient or attempt == _RETRIES - 1 or not retry:
            raise err
        wait = _BACKOFF * 2 ** attempt
        log(f"transient error on {path} - retrying in {wait}s ({err})")
        time.sleep(wait)


_REDACT = []


# cp1252 lead bytes of UTF-8 that got decoded as cp1252 somewhere upstream.
_MANGLED = ("\u00c2", "\u00c3", "\u00e2")


def _demojibake(s):
    """Undo one round of UTF-8 bytes read back as cp1252.

    Captions are hand-authored upstream and have come through a cp1252 step
    more than once -- every em-dash arriving as a three-character smear. 106 of
    them reached live posts before anyone caught it (2026-08-21), and the
    repost slot kept re-serving the same garbage. A caption cannot be edited
    once a reel is published, so scrub on the way in rather than trusting
    whatever wrote the queue.

    Only touches text that carries one of the tell-tale lead characters, and
    only when the round trip actually decodes -- clean text is returned as-is.
    """
    if not any(c in s for c in _MANGLED):
        return s
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def load_queue():
    if not QUEUE.exists():
        sys.exit(f"No queue at {QUEUE}")
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    for item in q.get("items", []):
        for field in ("caption", "title"):
            if isinstance(item.get(field), str):
                item[field] = _demojibake(item[field])
    return q


def save_queue(q):
    """Temp file then replace, so a crash mid-write cannot corrupt the queue."""
    tmp = QUEUE.with_suffix(".tmp")
    tmp.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(QUEUE)


SLOTS = ((9, "9:00a"), (13, "1:00p"), (18, "6:00p"))


def wants_old(index, olds_today):
    """Should the post at `index` in today's run be back-catalog?

    The middle slot is the repost slot and it is the only one -- which is just
    2 fresh : 1 reformat spelled out. `index >= 1` rather than `== 1` so that a
    day whose 1pm slot had to fall back to fresh still gets its repost at 6pm
    instead of silently dropping to 3-fresh and draining the fresh pool faster.
    """
    return olds_today < OLD_PER_DAY and index >= 1


def plan(pending, start, days, skip=0):
    """Project the next `days` of the board as (date, slot label, item).

    The same choice the live run makes, walked forward on paper. The phone board
    renders this, so a board that disagrees with the publisher is no longer
    possible by construction -- it did disagree through 8/13-8/15, which is how
    three straight reposts reached Instagram without the board ever showing it.
    """
    left, out = list(pending), []
    for d in range(days):
        day = start + timedelta(days=d)
        olds = 0
        for n, (_, label) in enumerate(SLOTS):
            if d == 0 and n < skip:
                continue
            if not left:
                return out
            prefer = wants_old(n, olds)
            item = next((i for i in left if is_old(i) == prefer), left[0])
            left.remove(item)
            olds += is_old(item)
            out.append((day, label, item))
    return out


def slot_target(now):
    """How many posts should be on the board by the end of THIS run.

    The contract is three a day, not three fixed clock times. Each run tops the
    day up to its target, so a slot that never fired is made up by the next one
    rather than silently lost -- that is the whole point. Morning aims for one,
    midday for two, and everything from late afternoon on aims for the full
    three, which is what makes the late safety-net run able to rescue a day
    where both earlier slots died.
    """
    if now.hour < 12:
        return 1
    if now.hour < 17:
        return 2
    return POSTS_PER_DAY


TOPIC_RANK = {"utility": 0, "talk": 1, "meta": 2}


def topic_class(item):
    """utility | talk | meta, off the queue field with a prefix fallback.

    The 8/25 review cut 36 posts by topic: utility medians 10.5, talk 1.5, meta
    2.0. Twelve talk posts and not one cleared 5 likes, at any hour, fresh or
    reposted -- while fresh-vs-back-catalog, the axis the mix rule is written
    on, came out 11.0 against 10.0. Topic is the axis that predicts; origin is
    not.
    """
    tc = item.get("topic_class")
    if tc in TOPIC_RANK:
        return tc
    stem = item["file"].rsplit(".", 1)[0]
    return "talk" if stem.startswith("ig-yt-") else "utility"


def _by_topic(pending):
    """Stable-sort the pending block so utility comes first, meta last.

    NOT a filter, and that distinction is the whole design. Utility supply runs
    about 1.1 reels/day against a contract of 3, so gating on topic would starve
    the queue and cost posts -- and three a day is Nick's non-negotiable, the
    one thing that does not get traded for a better median. Same doctrine as
    the fresh/back-catalog preference below it: prefer, fall back, never gap.

    Sorting rather than filtering also means the talk backlog still ships; it
    just stops being what the machine reaches for first.
    """
    return sorted(pending, key=lambda i: TOPIC_RANK[topic_class(i)])


def claim_next(q, prefer_old):
    """The next pending item, preferring the kind this slot is owed.

    Queue ORDER used to decide everything, and that is exactly what put three
    reformatted back-catalog reels on the board on 8/15: the pending block ran
    four fresh cuts and then sixteen DIY reposts in a row, so a whole day landed
    inside the old block. (The `"slot": 13` field some rows carry was meant to
    fence reposts into the 1pm slot -- nothing ever read it.) Order still picks
    which reel OF A KIND goes next; kind now decides the mix.

    Falls back to the other kind when the preferred one is empty. A dry fresh
    pool must never cost a post -- three a day is the contract, and Nick would
    rather see a repost than a gap.

    ponytail: the old per-item `earliest` date gate is gone. Its job was to stop
    the queue eating itself a day early, and the 3-a-day cap already does that
    job -- keeping both meant a missed slot could NOT be made up, because
    tomorrow's reel was fenced off behind its own date. The `earliest` field is
    left in queue.json (harmless, and the board still displays it) but nothing
    reads it now.

    No staging lock here: the workflow sets `concurrency` so two runs cannot
    overlap, which is a stronger guarantee than the lock it replaces (a crashed
    run used to leave an item wedged in 'staging' until a timeout reclaimed it).
    """
    pending = _by_topic([i for i in q["items"] if i.get("status") == "pending"])
    for item in pending:
        if is_old(item) == prefer_old:
            return item
    return pending[0] if pending else None


def publish_ig(item, url, tok, ig, dry_run):
    params = {"media_type": "REELS", "video_url": url,
              "caption": item["caption"], "access_token": tok}
    # Frame one is the thumbnail, and a MINED reel starts wherever its first
    # sentence started -- often mid-blink or looking away. thumb_offset lets the
    # cover come from anywhere in the reel without touching the edit. Set
    # "cover_ms" on the queue item (pick_cover.py shortlists candidates).
    if item.get("cover_ms"):
        params["thumb_offset"] = int(item["cover_ms"])
    cid = call("POST", f"{ig}/media", params)["id"]

    for _ in range(60):
        time.sleep(5)
        code = call("GET", cid, {"fields": "status_code",
                                 "access_token": tok}).get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"Meta could not process {item['file']}")
    else:
        raise RuntimeError(f"timed out waiting on {item['file']}")

    if dry_run:
        log(f"DRY RUN ok - container {cid} ready, not published")
        return None

    media_id = call("POST", f"{ig}/media_publish",
                    {"creation_id": cid, "access_token": tok}, retry=False)["id"]
    return call("GET", media_id, {"fields": "permalink",
                                  "access_token": tok}).get("permalink", media_id)


def publish_fb(local_path, caption, tok):
    """Three-phase Reels Publishing API: start -> upload bytes -> finish.

    Bytes, not file_url: the hosted-URL pull returned 422 on 8/10. In Actions the
    mp4 is already in the checkout, so there is nothing to download.
    """
    vid = call("POST", f"{FB_PAGE_ID}/video_reels",
               {"upload_phase": "start", "access_token": tok})["video_id"]
    blob = Path(local_path).read_bytes()
    req = urllib.request.Request(
        f"https://rupload.facebook.com/video-upload/v21.0/{vid}",
        data=blob, method="POST",
        headers={"Authorization": f"OAuth {tok}", "offset": "0",
                 "file_size": str(len(blob))})
    with urllib.request.urlopen(req, timeout=600) as r:
        if not json.load(r).get("success"):
            raise RuntimeError("facebook upload phase did not report success")
    call("POST", f"{FB_PAGE_ID}/video_reels", {
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
        "description": caption, "access_token": tok})
    return vid


def prune(q):
    """Delete mp4s every queue entry agrees are posted. The platform is the archive.

    GitHub Pages caps a site at 1GB and this repo was already at 811MB on 8/11.
    Guarded on ALL entries for a filename, because the same file has been queued
    twice before (ig-0811-otdv2, caught 8/12) and one posted row must not delete
    a file another row still needs.
    """
    status = {}
    for i in q["items"]:
        status.setdefault(i["file"], set()).add(i.get("status"))
    freed, gone = 0, []
    for name, states in status.items():
        if states == {"posted"}:
            f = REPO / name
            if f.exists():
                freed += f.stat().st_size
                f.unlink()
                gone.append(name)
    if gone:
        log(f"pruned {len(gone)} posted reels, freed {freed // (1 << 20)}MB")
    return gone


def publish_one(item, q, c, dry_run):
    """Post one queued reel to IG (then the FB page). True if IG accepted it.

    The queue is saved the moment IG succeeds, before Facebook is attempted, so
    a crash between the two surfaces can never re-post the reel to Instagram.
    """
    log(f"staging {item['file']}")
    try:
        link = publish_ig(item, RAW_BASE + item["file"],
                          c["META_ACCESS_TOKEN"], c["IG_USER_ID"], dry_run)
    except (RuntimeError, urllib.error.URLError) as e:
        # leave it pending so the next slot retries it, and say why out loud
        log(f"IG FAILED, left pending: {e}")
        return False

    if dry_run:
        return True

    item["status"] = "posted"
    item["permalink"] = link
    item["posted_at"] = datetime.now(TZ).isoformat(timespec="seconds")
    save_queue(q)
    log(f"PUBLISHED {item['file']} -> {link}")

    # The Facebook page is a bonus surface. A failure here must never wedge IG.
    if c.get("META_PAGE_TOKEN"):
        try:
            vid = publish_fb(REPO / item["file"], item["caption"], c["META_PAGE_TOKEN"])
            item["fb_page_video_id"] = vid
            save_queue(q)
            log(f"FB PAGE PUBLISHED {item['file']} -> video_id={vid}")
        except BaseException as e:
            log(f"FB PAGE FAILED (IG post unaffected): {type(e).__name__}: {e}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="Post one now even if this slot is already at target. "
                         "Manual dispatch only -- the 3-a-day cap below still holds, "
                         "so this pulls a later slot forward, it does not add a 4th post.")
    a = ap.parse_args()

    q = load_queue()
    pending = [i for i in q["items"] if i.get("status") == "pending"]

    if a.status:
        posted = sum(1 for i in q["items"] if i.get("status") == "posted")
        fresh = [i for i in pending if not is_old(i)]
        old = [i for i in pending if is_old(i)]
        today = datetime.now(TZ).date()
        # Cover is whichever side runs out first: the mix degrades to all
        # back-catalog the day the fresh pool empties, which is the number that
        # actually matters. Reporting total depth alone hides that entirely.
        days = min(len(fresh) // FRESH_PER_DAY, len(old) // OLD_PER_DAY)
        print(f"queue depth: {len(pending)} pending "
              f"({len(fresh)} fresh, {len(old)} back-catalog), {posted} posted")
        print(f"mix {FRESH_PER_DAY} fresh : {OLD_PER_DAY} reformat per day")
        print(f"  fresh cover:   {len(fresh) // FRESH_PER_DAY} days "
              f"-- dry {(today + timedelta(days=len(fresh) // FRESH_PER_DAY)).isoformat()}")
        print(f"  catalog cover: {len(old) // OLD_PER_DAY} days "
              f"-- dry {(today + timedelta(days=len(old) // OLD_PER_DAY)).isoformat()}")
        print(f"  mix holds for {days} day{'' if days == 1 else 's'}, "
              f"then falls back to whatever is left")
        now = datetime.now(TZ)
        gone = sum(1 for h, _ in SLOTS if h <= now.hour)
        for day, label, item in plan(pending, today, 4, skip=gone):
            print(f"  {day}  {label:<8} {item['file']:<26} {item.get('title', '')}")
        return

    if a.prune:
        prune(q)
        return

    now = datetime.now(TZ)
    today = now.date().isoformat()
    posted_today = [i for i in q["items"] if i.get("status") == "posted"
                    and str(i.get("posted_at", "")).startswith(today)]
    done = len(posted_today)
    olds_today = sum(1 for i in posted_today if is_old(i))
    owed = max(0, slot_target(now) - done)
    if a.force and not owed and done < POSTS_PER_DAY:
        # Manual override for a live demo: the slot clock says wait, but the day
        # still owes a post. Pull it forward rather than adding one -- the
        # 3-a-day contract is the invariant, the clock times are only spacing.
        owed = 1
        log(f"--force: slot target met but only {done}/{POSTS_PER_DAY} posted today "
            f"-> pulling the next slot forward")
    if a.dry_run:
        owed = min(owed, 1)   # a dry run never marks posted, so it would restage item 1
    log(f"{done} posted today ({olds_today} back-catalog), "
        f"this slot targets {slot_target(now)} -> posting {owed}")
    if not owed:
        log("already at target for this slot - nothing to do")
        return
    fresh = [i for i in pending if not is_old(i)]
    if len(pending) < POSTS_PER_DAY * 2:
        log(f"LOW QUEUE: {len(pending)} reels = "
            f"{len(pending) // POSTS_PER_DAY} days of cover. Refill the queue.")
    # The mix is the thing that silently degrades: the total can look healthy
    # while the fresh side is empty and every slot falls back to a repost.
    if len(fresh) < FRESH_PER_DAY * 2:
        log(f"LOW FRESH: {len(fresh)} fresh cuts = "
            f"{len(fresh) // FRESH_PER_DAY} days at {FRESH_PER_DAY}/day. "
            f"Drop raws in Reels drop or the board goes all back-catalog.")
    # Utility is the supply that actually decides how the day performs: it
    # medians 10.5 against 1.5 for talk (8/25 review, n=32). When it runs out
    # the machine still posts -- three a day is the contract -- it just posts
    # the category that has never cleared 5 likes. That is worth saying out
    # loud, because it is the one shortage a garage afternoon fixes.
    utility = [i for i in pending if topic_class(i) == "utility"]
    if len(utility) < POSTS_PER_DAY:
        log(f"LOW UTILITY: {len(utility)} utility reels left of {len(pending)} "
            f"pending. Below a day of cover -- the board falls back to talk, "
            f"which medians 1.5. One shoot of hands-and-tools clips fixes it.")

    c = creds()
    _REDACT.extend([c["META_ACCESS_TOKEN"], c.get("META_PAGE_TOKEN", "")])

    failed = False
    for n in range(owed):
        # `done + n` is this post's index in the DAY, not in the run, so a
        # catch-up run that fires all three still lands fresh / repost / fresh.
        item = claim_next(q, wants_old(done + n, olds_today))
        if not item:
            log("QUEUE EMPTY - nothing left to post. Refill via the reel loop.")
            break
        if is_old(item):
            olds_today += 1
        if n:
            # Two reels inside one catch-up run go out spaced, not back to back.
            log(f"waiting {CATCHUP_GAP}s before the next catch-up post")
            time.sleep(CATCHUP_GAP)
        log(f"slot {done + n + 1}/{POSTS_PER_DAY}: "
            f"{'back-catalog' if is_old(item) else 'FRESH'}")
        if not publish_one(item, q, c, a.dry_run):
            # A bad token or a dead network fails every remaining item the same
            # way, so stop rather than burn the queue against a broken pipe.
            failed = True
            break

    prune(q)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
