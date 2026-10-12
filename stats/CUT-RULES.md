# CUT RULES — read before you cut. Generated; never hand-edit.

_Written by `publisher/craft_report.py` on **2026-10-12** from **202** posted reels (median retention = share of the reel actually watched). Rewritten every run, so a hand edit dies at the next one — change the data or the code. Full tables: `CRAFT.md`. **Where this file and SAM-PLAYBOOK.md disagree, this file wins.**_

**Stale check:** if that date is more than 8 days old, say so in the delivery, then run `python publisher/stats.py && python publisher/craft_report.py` and COMMIT both files — an uncommitted re-run is erased by the next checkout (the n=100 run was, 9/08).

## Levers, biggest first

1. **duration** — **LEVER** — favour **under 20s**, 36 pts over over 70s; views agree. under 20s 49% (n=76) · 20-35s 31% (n=52) · 35-50s 26% (n=38) · 50-70s 19% (n=24) · over 70s 13% (n=12). Retention falls at EVERY step longer: cut to the number, not the material.
2. **topic** — **LEVER** — favour **utility**, 16 pts over talk; views agree. utility 44% (n=102) · meta 29% (n=10) · talk 28% (n=90)
3. **fresh/catalog** — **LEVER** — favour **back-catalog**, 13 pts over fresh; views agree. back-catalog 45% (n=64) · fresh 31% (n=138)
4. **cover** — **NO LEVER** — 3 pts is noise; spend no effort here. custom cover 37% (n=111) · default cover 33% (n=91)
5. **collab** — **TOO THIN** — not enough posts on both sides to act on. collab 37% (n=6, thin) · solo 35% (n=196)

**Standing exception — hands-and-tools how-tos run 35-60s** (Nick, 2026-10-05). The duration lever above is % watched; for utility, watch seconds grow with length. Rules: Rook `_Skills/reel-loop.md` §3a.

_LEVER = at least 5 pts between two buckets that each have 10+ posts. Thin buckets are shown so you can see them coming, never acted on._
