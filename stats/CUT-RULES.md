# CUT RULES — read before you cut. Generated; never hand-edit.

_Written by `publisher/craft_report.py` on **2026-09-11** from **109** posted reels (median retention = share of the reel actually watched). Rewritten every run, so a hand edit dies at the next one — change the data or the code. Full tables: `CRAFT.md`. **Where this file and SAM-PLAYBOOK.md disagree, this file wins.**_

**Stale check:** if that date is more than 8 days old, say so in the delivery, then run `python publisher/stats.py && python publisher/craft_report.py` and COMMIT both files — an uncommitted re-run is erased by the next checkout (the n=100 run was, 9/08).

## Levers, biggest first

1. **duration** — **LEVER** — favour **under 20s**, 35 pts over over 70s; views agree. under 20s 48% (n=11) · 20-35s 31% (n=32) · 35-50s 28% (n=33) · 50-70s 17% (n=22) · over 70s 13% (n=11). Retention falls at EVERY step longer: cut to the number, not the material.
2. **topic** — **LEVER** — favour **utility**, 19 pts over talk; views agree. utility 37% (n=52) · meta 23% (n=7, thin) · talk 18% (n=50)
3. **fresh/catalog** — **LEVER** — favour **back-catalog**, 12 pts over fresh; views agree. back-catalog 37% (n=31) · fresh 24% (n=78)
4. **cover** — **NO LEVER** — 1 pts is noise; spend no effort here. custom cover 29% (n=44) · default cover 28% (n=65)
5. **collab** — **TOO THIN** — not enough posts on both sides to act on. collab 35% (n=5, thin) · solo 28% (n=104)

_LEVER = at least 5 pts between two buckets that each have 10+ posts. Thin buckets are shown so you can see them coming, never acted on._
