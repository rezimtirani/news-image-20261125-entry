# The World in One Day — 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/rezimtirani/news-image-20261125-entry/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/rezimtirani/news-image-20261125-entry/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One image that sums up 25 November 2026 in world news: a newspaper front
page drawn entirely by `main.py` — US spy agencies hit by a cyber breach,
Huawei convicted of stealing trade secrets, Zelenskyy confirms a ship
strike, and Houthis hit Riyadh's tallest tower.

> CIA and ODNI hit by cyber breach. Huawei guilty of stealing trade
> secrets. Zelenskyy confirms a ship strike. Houthis hit Riyadh tower.

## How it works

`main.py` (Python 3 standard library only — no Pillow, no network) paints
the front page pixel by pixel onto a canvas, renders the headlines with a
small bitmap font defined in the file, and encodes the PNG by hand with
`zlib`. It is fully deterministic: two runs write identical bytes.

```sh
python3 main.py
```

It writes `entry.png` (1024x1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR`,
after verifying the PNG magic, the IEND trailer, the dimensions and the
size limit.

## License

MIT — see [LICENSE](LICENSE).
