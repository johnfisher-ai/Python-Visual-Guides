"""Build the library front page: what this is, and every guide in reading order."""

import sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import page                                          # noqa: E402
from tools.manifest import load                                 # noqa: E402
from tools.build_guide import STATUS                            # noqa: E402


def band_rows(guides):
    out, band = [], None
    for g in guides:
        if g.band != band:
            band = g.band
            out.append(f'<tr class="band"><td colspan="4">{e(band)}</td></tr>')
        label, cls = STATUS[g.status]
        link = (f'<a href="{g.page}">{e(g.title)}</a>'
                if (page.PUBLIC / g.page).exists() else e(g.title))
        out.append(
            f'<tr><td class="n">{g.number}</td>'
            f'<td class="t"><b>{link}</b><span>{e(g.subtitle)}</span></td>'
            f'<td class="c">{len(g.notebooks)}</td>'
            f'<td class="s"><span class="badge {cls}">{e(label)}</span></td></tr>')
    return "".join(out)


def build():
    site, guides = load()
    total = sum(len(g.notebooks) for g in guides)
    written = sum(g.written for g in guides)

    body = page.head(
        filename="index.html",
        title=site["title"],
        tab_title=site["title"],
        description=site["tagline"],
        card_title=site["title"],
        card_desc=site["tagline"],
        kicker="A library of interactive Python guides",
        byline="By John Fisher. Every guide is a set of Colab notebooks you run.",
    )
    body += f"""
  <section>
    <p class="lede">{e(site['tagline'])} The explanation, the code, the output and the figures
    all live in the notebook. These pages exist only to get you to the right one.</p>

    <div class="figures">
      <div><span class="n">{len(guides)}</span><span class="l">guides</span></div>
      <div><span class="n">{total}</span><span class="l">notebooks planned</span></div>
      <div><span class="n">{written}</span><span class="l">written so far</span></div>
      <div><span class="n">0</span><span class="l">setup required. It runs in a browser</span></div>
    </div>

    <div class="note">
      <p><strong>How to use this.</strong> Every notebook opens in Google Colab and runs with
      no installation. Read it on GitHub first if you prefer, then open it and change
      something. The exercises are the point: there is a separate solutions notebook for each,
      so nothing is spoiled by sitting next to the question.</p>
    </div>
  </section>

  <section>
    <h2>The guides</h2>
    <p>Three bands. The spine teaches the language, the library guides teach the tools, and the
    projects put both to work. Inside the spine, each guide assumes the one before it.</p>
    <div class="scroll">
      <table class="guides"><tbody>{band_rows(guides)}</tbody></table>
    </div>
  </section>
"""
    body += page.foot("index.html")
    page.write("index.html", body)


if __name__ == "__main__":
    build()
