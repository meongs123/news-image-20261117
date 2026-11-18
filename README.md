[![news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/meongs123/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/meongs123/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117)

# The World in One Page — Tuesday 17 November 2026

One image that sums up the world's news of Tuesday 17 November 2026, as an
editorial front page: masthead with the date and story count, a numbered
world map of the six leads, six lead cards with flat programmatic icons, an
"ALSO ON THIS PAGE" list of 18 more stories, a "BY THE NUMBERS" strip, and
a source line. 24 stories, 5 continents.

## How it is made

`compose.py` draws the whole page with PIL (DejaVu fonts, system install):
no photos, no AI images, no network — every icon, map shape and letter is
drawn here from code, so the output is fully deterministic (identical bytes
on every run). `main.py` (standard library only) copies the committed
`entry.png` to `/output/entry.png` for the grader.

```sh
python3 compose.py        # writes entry.png (1024x1024 PNG, <1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Stories (all verified against real reporting)

Leads: Kerch Bridge road span falls in a Ukrainian strike; Trump lands in
Manila for the Quad and a Thailand trade deal; a third U.S. carrier reaches
the Gulf as tankers are hit near Hormuz; a JPMorgan software bug slows U.S.
banking and Zelle; five EU states plan a Rwanda return hub; WHO validates
Eritrea's elimination of trachoma. Plus 18 more in the ALSO list, from the
Vulcan failure and Nvidia's $115.8B quarter to Ebola passing 11,000 cases
in DR Congo. Disputed claims are hedged ("Iran says", "Russia says").

## License

MIT. All drawings and text are original work.
