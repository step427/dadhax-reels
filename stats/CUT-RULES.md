# CUT RULES — read before you cut. Generated; never hand-edit.

_Written by `publisher/craft_report.py` on **2026-10-23** from **235** posted reels (median retention = share of the reel actually watched). Rewritten every run, so a hand edit dies at the next one — change the data or the code. Full tables: `CRAFT.md`. **Where this file and SAM-PLAYBOOK.md disagree, this file wins.**_

**Stale check:** if that date is more than 8 days old, say so in the delivery, then run `python publisher/stats.py && python publisher/craft_report.py` and COMMIT both files — an uncommitted re-run is erased by the next checkout (the n=100 run was, 9/08).

## Levers, biggest first

1. **duration** — **LEVER** — favour **under 20s**, 35 pts over over 70s; views agree. under 20s 48% (n=89) · 20-35s 31% (n=62) · 35-50s 27% (n=45) · 50-70s 20% (n=27) · over 70s 13% (n=12). Retention falls at EVERY step longer: cut to the number, not the material.
2. **topic** — **LEVER** — favour **utility**, 15 pts over talk; views agree. utility 43% (n=132) · meta 29% (n=10) · talk 28% (n=93)
3. **fresh/catalog** — **LEVER** — favour **back-catalog**, 10 pts over fresh; views agree. back-catalog 44% (n=73) · fresh 33% (n=162)
4. **cover** — **NO LEVER** — 2 pts is noise; spend no effort here. custom cover 38% (n=130) · default cover 36% (n=105)
5. **collab** — **TOO THIN** — not enough posts on both sides to act on. collab 36% (n=6, thin) · solo 36% (n=229)

**Standing exception — hands-and-tools how-tos run 35-60s** (Nick, 2026-10-05). The duration lever above is % watched; for utility, watch seconds grow with length. Rules: Rook `_Skills/reel-loop.md` §3a.

_LEVER = at least 5 pts between two buckets that each have 10+ posts. Thin buckets are shown so you can see them coming, never acted on._
