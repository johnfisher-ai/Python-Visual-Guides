# Social cards

Source HTML and rendered PNGs for the social preview images. Nothing here is published:
GitHub Pages serves `public/` only.

| File | Size | Used for |
|---|---|---|
| `linkedin-card.png` | 1200x627 | Open Graph image. Copied to `public/assets/img/social-card.png`, which every page references via `og:image`. Covers LinkedIn, Facebook, Slack and Twitter. |
| `github-card.png` | 1280x640 | The repository's social preview. Upload by hand under Settings > Social preview; GitHub has no API for it. |

Edit the text in each `card-*.html`, then:

```bash
bash assets/social/render.sh
```

`render.sh` uses Google Chrome on a Mac, the Chromium a Claude Code cloud session has at
`/opt/pw-browsers/chromium`, or whatever `CHROME` names.

The cards say nothing that changes as guides are added: no guide or notebook counts. Keep it
that way, because a stale number in an image goes unnoticed for months.

The font stacks put Iowan Old Style and Charter first, which a Mac has, and Caladea, Inter and
DejaVu Sans Mono after them, which a cloud session has. The cards committed on October 28, 2026
were rendered in a cloud session, so they show Caladea and Inter. The Bitstream Charter that
Linux ships is a Type 1 font, which Chromium cannot use.

`tools/page.py` holds the image's description (`CARD_ALT`), which every page sends as
`og:image:alt`. Change it when the card's text changes.

## After changing the Open Graph image

Platforms cache previews. Re-scrape with the
[LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) or the card will keep
showing the old one, or nothing at all if the first fetch predated the image.

## If the dimensions change

`og:image:width` and `og:image:height` are written into every page. Update them together,
or the declared size will not match the file.
