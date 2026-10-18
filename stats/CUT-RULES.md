# CUT RULES — read before you cut. Generated; never hand-edit.

_Written by `publisher/craft_report.py` on **2026-10-18** from **220** posted reels (median retention = share of the reel actually watched). Rewritten every run, so a hand edit dies at the next one — change the data or the code. Full tables: `CRAFT.md`. **Where this file and SAM-PLAYBOOK.md disagree, this file wins.**_

**Stale check:** if that date is more than 8 days old, say so in the delivery, then run `python publisher/stats.py && python publisher/craft_report.py` and COMMIT both files — an uncommitted re-run is erased by the next checkout (the n=100 run was, 9/08).

## Levers, biggest first

1. **duration** — **LEVER** — favour **under 20s**, 35 pts over over 70s; views agree. under 20s 48% (n=84) · 20-35s 31% (n=56) · 35-50s 27% (n=43) · 50-70s 19% (n=25) · over 70s 13% (n=12). Retention falls at EVERY step longer: cut to the number, not the material.
2. **topic** — **LEVER** — favour **utility**, 15 pts over talk; views agree. utility 43% (n=119) · meta 29% (n=10) · talk 28% (n=91)
3. **fresh/catalog** — **LEVER** — favour **back-catalog**, 12 pts over fresh; views agree. back-catalog 44% (n=70) · fresh 32% (n=150)
4. **cover** — **NO LEVER** — 3 pts is noise; spend no effort here. custom cover 37% (n=126) · default cover 34% (n=94)
5. **collab** — **TOO THIN** — not enough posts on both sides to act on. collab 36% (n=6, thin) · solo 35% (n=214)

**Standing exception — hands-and-tools how-tos run 35-60s** (Nick, 2026-10-05). The duration lever above is % watched; for utility, watch seconds grow with length. Rules: Rook `_Skills/reel-loop.md` §3a.

_LEVER = at least 5 pts between two buckets that each have 10+ posts. Thin buckets are shown so you can see them coming, never acted on._
