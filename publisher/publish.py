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


def call(method, path, params):
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{GRAPH}/{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # the body can echo the query string back, token included -- never log it raw
        body = e.read().decode()[:400]
        for secret in _REDACT:
            if secret:
                body = body.replace(secret, "<redacted>")
        raise RuntimeError(f"Graph API error {e.code} on {path}: {body}")


_REDACT = []


def load_queue():
    if not QUEUE.exists():
        sys.exit(f"No queue at {QUEUE}")
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def save_queue(q):
    """Temp file then replace, so a crash mid-write cannot corrupt the queue."""
    tmp = QUEUE.with_suffix(".tmp")
    tmp.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(QUEUE)


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


def claim_next(q):
    """The next pending item, in queue order.

    ponytail: the old per-item `earliest` date gate is gone. Its job was to stop
    the queue eating itself a day early, and the 3-a-day cap already does that
    job -- keeping both meant a missed slot could NOT be made up, because
    tomorrow's reel was fenced off behind its own date. The `earliest` field is
    left in queue.json (harmless, and the board still displays it) but nothing
    reads it now. Queue ORDER is the schedule.

    No staging lock here: the workflow sets `concurrency` so two runs cannot
    overlap, which is a stronger guarantee than the lock it replaces (a crashed
    run used to leave an item wedged in 'staging' until a timeout reclaimed it).
    """
    for item in q["items"]:
        if item.get("status") == "pending":
            return item
    return None


def publish_ig(item, url, tok, ig, dry_run):
    cid = call("POST", f"{ig}/media", {
        "media_type": "REELS", "video_url": url,
        "caption": item["caption"], "access_token": tok,
    })["id"]

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
                    {"creation_id": cid, "access_token": tok})["id"]
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
    a = ap.parse_args()

    q = load_queue()
    pending = [i for i in q["items"] if i.get("status") == "pending"]

    if a.status:
        posted = sum(1 for i in q["items"] if i.get("status") == "posted")
        days, rem = divmod(len(pending), POSTS_PER_DAY)
        today = datetime.now(TZ).date()
        dry = today + timedelta(days=days)
        print(f"queue depth: {len(pending)} pending, {posted} posted")
        print(f"cover at {POSTS_PER_DAY}/day: {days} full days"
              f"{f' + {rem}' if rem else ''} -- runs dry {dry.isoformat()}")
        for n, i in enumerate(pending[:9]):
            print(f"  {today + timedelta(days=n // POSTS_PER_DAY)}  "
                  f"{i['file']:<26} {i.get('title', '')}")
        return

    if a.prune:
        prune(q)
        return

    now = datetime.now(TZ)
    today = now.date().isoformat()
    done = sum(1 for i in q["items"] if i.get("status") == "posted"
               and str(i.get("posted_at", "")).startswith(today))
    owed = max(0, slot_target(now) - done)
    if a.dry_run:
        owed = min(owed, 1)   # a dry run never marks posted, so it would restage item 1
    log(f"{done} posted today, this slot targets {slot_target(now)} -> posting {owed}")
    if not owed:
        log("already at target for this slot - nothing to do")
        return
    if len(pending) < POSTS_PER_DAY * 2:
        log(f"LOW QUEUE: {len(pending)} reels = "
            f"{len(pending) // POSTS_PER_DAY} days of cover. Refill the queue.")

    c = creds()
    _REDACT.extend([c["META_ACCESS_TOKEN"], c.get("META_PAGE_TOKEN", "")])

    failed = False
    for n in range(owed):
        item = claim_next(q)
        if not item:
            log("QUEUE EMPTY - nothing left to post. Refill via the reel loop.")
            break
        if n:
            # Two reels inside one catch-up run go out spaced, not back to back.
            log(f"waiting {CATCHUP_GAP}s before the next catch-up post")
            time.sleep(CATCHUP_GAP)
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
