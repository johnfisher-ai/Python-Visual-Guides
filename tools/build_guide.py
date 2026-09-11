"""Build one thin page per guide: an introduction and an index of its notebooks.

The page is a doorway. It carries no explanation, no code and no output, because
all of that belongs in the notebook. If a sentence here would be better with a
cell under it, it is in the wrong file.
"""

import sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import page                                          # noqa: E402
from tools.manifest import load                                 # noqa: E402

STATUS = {
    "building":  ("Being written", "st-building"),
    "planned":   ("Planned", "st-planned"),
    "published": ("Complete", "st-done"),
}

# The labels on each notebook's links. The sentence over the table names them,
# so both read from here and cannot disagree.
RUN, READ, SOLUTIONS = "Open in Colab", "Read", "Solutions"


def rows(g):
    if not any(nb.exists for nb in g.notebooks):
        return "".join(
            f'<tr class="soon"><td class="n">{nb.n}</td>'
            f'<td class="t"><b>{e(nb.title)}</b><span>{e(nb.blurb)}</span></td>'
            f'<td class="go">not yet written</td></tr>'
            for nb in g.notebooks)
    out = []
    for nb in g.notebooks:
        if nb.exists:
            colab = page.COLAB + f"notebooks/{g.slug}/{nb.filename}"
            read = f"{page.REPO}/blob/main/notebooks/{g.slug}/{nb.filename}"
            go = (f'<a class="run" href="{colab}">{RUN}</a>'
                  f'<a class="read" href="{read}">{READ}</a>')
            # Solutions are linked, but quietly: the reader should meet the
            # exercise before the answer.
            if nb.solutions.exists():
                sol = page.COLAB + f"notebooks/{g.slug}/{nb.solutions.name}"
                go += f'<a class="sol" href="{sol}">{SOLUTIONS}</a>'
            cls = ""
        else:
            go, cls = "not yet written", ' class="soon"'
        out.append(f'<tr{cls}><td class="n">{nb.n}</td>'
                   f'<td class="t"><b>{e(nb.title)}</b><span>{e(nb.blurb)}</span></td>'
                   f'<td class="go">{go}</td></tr>')
    return "".join(out)


def how_to_open(g):
    """What the links in the table do, by the names the reader sees on them."""
    if not any(nb.exists for nb in g.notebooks):
        return "None of these notebooks is written yet. This is the plan, in reading order."
    return (f"<b>{RUN}</b> runs a notebook in your browser, and <b>{READ}</b> shows it on "
            f"GitHub without running it. Every notebook runs on its own, and the answers to its "
            f"exercises are in a separate notebook, linked as <b>{SOLUTIONS}</b>.")


def build_one(site, g):
    label, cls = STATUS[g.status]
    body = page.head(
        filename=g.page,
        title=g.title,
        tab_title=f"{g.title} · {site['title']}",
        description=g.intro,
        card_title=g.title,
        card_desc=g.intro,
        kicker=f"Guide {g.number} · {g.band}",
        byline=e(g.subtitle),
    )
    body += f"""
  <section>
    <p class="lede">{e(g.intro)}</p>
    <p class="meta"><span class="badge {cls}">{e(label)}</span>
       <span>{len(g.notebooks)} notebooks</span>
       <span>{g.written} written</span></p>
    <p class="pre"><b>Before this guide:</b> {e(g.prerequisites)}</p>
  </section>

  <section>
    <h2>The notebooks</h2>
    <p>{how_to_open(g)}</p>
    <div class="scroll">
      <table class="nbs"><tbody>{rows(g)}</tbody></table>
    </div>
  </section>
"""
    if g.credits:
        body += f"""
  <section class="credits">
    <h2>Sources</h2>
    <p>{g.credits}</p>
  </section>
"""

    body += page.foot(g.page)
    page.write(g.page, body)


def build():
    site, guides = load()
    for g in guides:
        build_one(site, g)


if __name__ == "__main__":
    build()
