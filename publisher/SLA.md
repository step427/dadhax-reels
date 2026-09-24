# The publisher is DONE. This is its contract.

Written 2026-08-25, after five consecutive days of engineering on a system that
had already been working since 8/07.

## Why this file exists

Between 8/21 and 8/25 the publisher got: a caption encoding fix, a transient
retry, a stats collector, a corrected statistical read, a tooling inventory, and
a topic preference. Two of those were real defects with real output damage. The
rest was work on the tractable thing.

Over the same stretch the Q3 scorecard line that is a solo build sat at 2,100% of
target while the two lines needing another human to say yes sat at zero. Nick's
own profile names this pattern: *building systems instead of executing deals.*

The machine is not the goal. **Nick recording is the goal, and the machine
exists so that recording is the only thing he has to do.** It already does that.

## The contract

| | |
|---|---|
| **3 posts/day, as a FLOOR** | Every day. Non-negotiable — a 5DNN identity commitment, not a performance lever, and never traded for a better median. **Amended 8/29:** three is the floor, not a ceiling (Nick, 8/28: *"i dont really care if i do more than 3/day. but the floor is 3 posts/day"*). The scheduled runs still top a day up TO three; `--force` and deliberate releases go on top. A day with five posts is not a breach — a day with two is. This line originally read as a ceiling and would have had the 8/28 Neighbors First collab release flagged as a contract violation. |
| **0 mangled captions** | `_demojibake` guards the load path. |
| **0 silent failures** | Transients retry; a run that cannot post says so in the log. |
| **Queue never under 7 days of cover** | Below that, `LOW QUEUE` / `LOW FRESH` / `LOW UTILITY` fire. |

**A breach of a line above is a bug. Fix it.**

**Anything not on that list is a feature. It is frozen.**

## What "frozen" rules out

Tuning that chases likes on a 260-follower account. Posting-hour experiments —
topic outperforms hour by 7× and the hour effect is n=5. Any further slicing of
`stats/README.md`. Any optimisation whose best case is a handful more likes per
post, because there is no mechanism on this account by which likes become
dollars: no email capture, no offer, no product.

## What reopens the file

- A breach of the contract above.
- **The first inbound DM that turns into a conversation** — that is the first
  evidence the channel converts, and it changes what this thing is for.
- **1,000 followers.**

Until one of those, the publisher reports one line to the weekly L10 and nothing
else:

```
posts 21/21 · queue N days cover · silent failures: 0
```

It has earned the right to be a boring row.

## The constraint that is actually binding

Utility content medians 10.5 likes. Talk medians 1.5. Utility supply runs about
1.1 reels/day against a contract of 3.

**The bottleneck is hands-and-tools footage, and no amount of code fixes it.**
One garage afternoon at twenty hacks fills three weeks. That is the highest-
leverage content action available and it is not a software task.
