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
    first = guides[0]
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
    <p class="lede">Learn Python by running it. Every guide is a set of notebooks that open in
    Google Colab: read a little, run a cell, change it, run it again. Nothing to install and
    nothing to set up.</p>
    <p>New to Python? Start with <a href="{first.page}"><strong>{e(first.title)}</strong></a>.
    The guides below are in reading order.</p>

    <div class="figures">
      <div><span class="n">{len(guides)}</span><span class="l">guides</span></div>
      <div><span class="n">{total}</span><span class="l">notebooks planned</span></div>
      <div><span class="n">{written}</span><span class="l">written so far</span></div>
      <div><span class="n">0</span><span class="l">things to install</span></div>
    </div>

    <div class="note">
      <p><strong>How a notebook works.</strong> Open one and it runs in your browser. Each has
      the explanation, worked examples you can edit, exercises to try, and a section on the
      errors that part of Python actually produces, with the real message shown.</p>
      <p>The exercises are the point. Every notebook has a separate solutions file, so the
      answer is never sitting one scroll below the question.</p>
    </div>
  </section>

  <section>
    <h2>The guides</h2>
    <p>The first five teach the language itself, and are best worked through in order: each one
    assumes the one before it. The next five cover the libraries you will reach for once you can
    write Python. The last puts everything to work on real problems.</p>
    <div class="scroll">
      <table class="guides"><tbody>{band_rows(guides)}</tbody></table>
    </div>
  </section>
"""
    body += page.foot("index.html")
    page.write("index.html", body)


if __name__ == "__main__":
    build()
