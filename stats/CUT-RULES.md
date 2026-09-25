# CUT RULES — read before you cut. Generated; never hand-edit.

_Written by `publisher/craft_report.py` on **2026-09-25** from **151** posted reels (median retention = share of the reel actually watched). Rewritten every run, so a hand edit dies at the next one — change the data or the code. Full tables: `CRAFT.md`. **Where this file and SAM-PLAYBOOK.md disagree, this file wins.**_

**Stale check:** if that date is more than 8 days old, say so in the delivery, then run `python publisher/stats.py && python publisher/craft_report.py` and COMMIT both files — an uncommitted re-run is erased by the next checkout (the n=100 run was, 9/08).

## Levers, biggest first

1. **duration** — **LEVER** — favour **under 20s**, 33 pts over over 70s; views agree. under 20s 46% (n=44) · 20-35s 31% (n=40) · 35-50s 27% (n=34) · 50-70s 17% (n=22) · over 70s 13% (n=11). Retention falls at EVERY step longer: cut to the number, not the material.
2. **topic** — **LEVER** — favour **utility**, 15 pts over talk; views agree. utility 41% (n=72) · meta 34% (n=9, thin) · talk 26% (n=70)
3. **fresh/catalog** — **LEVER** — favour **back-catalog**, 13 pts over fresh; views agree. back-catalog 41% (n=48) · fresh 29% (n=103)
4. **cover** — **NO LEVER** — 3 pts is noise; spend no effort here. custom cover 34% (n=72) · default cover 30% (n=79)
5. **collab** — **TOO THIN** — not enough posts on both sides to act on. collab 36% (n=6, thin) · solo 32% (n=145)

_LEVER = at least 5 pts between two buckets that each have 10+ posts. Thin buckets are shown so you can see them coming, never acted on._
