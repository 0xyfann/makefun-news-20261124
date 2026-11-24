# makefun-news-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/0xyfann/makefun-news-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/0xyfann/makefun-news-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Deterministic 1024x1024 newspaper front page (PNG <= 1 MiB) summing up
Tuesday, 24 November 2026: 10 world-news stories across war, climate,
geopolitics, disaster, law, business, sport, and Gaza/Tech. Rendered by
`draw_news.py` with a hand-built 5x7 bitmap font in the standard library
only — no network, no randomness, no timestamps, so every run is
byte-identical. `main.py` regenerates the art and copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR` (or `/output`).

## What's inside

Masthead **THE GLOBAL HERALD**, the exact date line **Tuesday, 24 November
2026**, and ten sectioned stories with specific names and numbers: Ukraine's
sea-drone strike on the Merkury corvette in Benghazi; the collapsed COP31 in
Antalya; Iran's claimed Patriot strikes in Bahrain; the Indonesia candy
factory fire (24 dead); the Sparta II blaze in the Gulf of Finland; the Dymer
strikes (14 missing); the ICJ Rohingya genocide ruling; Jensen Huang's return
and Nvidia's 31% pop; Alcaraz, the Wellington Test draw and the Gukesh-Sindarov
chess match; and the Oxfam/CEOBS Gaza contamination report with the Waymo
pullback. Verified: two `main.py` runs to different output directories are
byte-identical, the PNG is 1024x1024 and <= 1 MiB.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=p1x954ca&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
