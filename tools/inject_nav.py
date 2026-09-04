#!/usr/bin/env python3
"""Put navigation into every notebook, top and bottom.

A reader who opens a notebook in Colab arrives with no way back. There is no site
around it, no contents, and no next. Without this they are using the back button,
which only works if they arrived from the site in the first place.

Two cells per notebook, both generated from the manifest and both replaced on every
run, so a change to the order or a title propagates rather than drifting:

  nav-top     breadcrumb to the library and the guide, then the title
  nav-bottom  previous, the guide contents, next

Written in that order and marked with cell tags, so this is safe to run repeatedly.

    python3 tools/inject_nav.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import page                                          # noqa: E402
from tools.manifest import load                                 # noqa: E402

TOP, BOTTOM = "nav-top", "nav-bottom"


def site_link(url: str, label: str) -> str:
    """A link that leaves Colab.

    Colab shows a Google interstitial for any link off google.com, and there is no
    way around it from inside a notebook. An HTML anchor with target="_blank" was
    tried and Colab strips the attribute, so the reader still loses their tab.
    Plain markdown it is: same behaviour, less machinery.

    Colab-to-Colab links, previous and next and back-to-notebook, stay on
    google.com and are unaffected.
    """
    return f"[{label}]({url})"





def colab(guide_slug: str, filename: str) -> str:
    return page.COLAB + f"notebooks/{guide_slug}/{filename}"


def guide_url(g) -> str:
    return f"{page.SITE}/{g.page}"


def cell(tag: str, text: str) -> dict:
    # nbformat 4.5 requires an id on every cell. A stable id derived from the tag
    # keeps the file from churning on every rebuild.
    return {"cell_type": "markdown", "id": f"site-{tag}", "metadata": {"tags": [tag]},
            "source": text.strip("\n") + "\n"}


def top_cell(site, g, nb, solutions: bool = False) -> dict:
    lib = site_link(f"{page.SITE}/", site["title"])
    guide = site_link(guide_url(g), g.title)
    heading = f"{nb.title} &middot; Solutions" if solutions else nb.title
    return cell(TOP, f"""
{lib} &nbsp;&rsaquo;&nbsp; {guide}

# {heading}
""")


def solutions_bottom_cell(site, g, nb) -> dict:
    """Solutions go back to their own notebook, not on to the next one.

    Somebody reading answers is mid-exercise, not moving through the guide, so
    previous and next would take them somewhere they did not ask to go.
    """
    back = f"&#8592; **Back to:** [{nb.title}]({colab(g.slug, nb.filename)})"
    contents = site_link(guide_url(g), f"{g.title} Notebooks")
    return cell(BOTTOM, "---\n\n" + f"{back}  &nbsp;&middot;&nbsp;  {contents}" + "\n")


def bottom_cell(site, g, nb) -> dict:
    prev_nb = next((x for x in g.notebooks if x.n == nb.n - 1), None)
    next_nb = next((x for x in g.notebooks if x.n == nb.n + 1), None)

    left = (f"&#8592; **Previous:** [{prev_nb.title}]({colab(g.slug, prev_nb.filename)})"
            if prev_nb and prev_nb.exists else "")
    right = (f"**Next:** [{next_nb.title}]({colab(g.slug, next_nb.filename)}) &#8594;"
             if next_nb and next_nb.exists else "")
    middle = site_link(guide_url(g), f"{g.title} Notebooks")

    parts = [p for p in (left, middle, right) if p]
    return cell(BOTTOM, "---\n\n" + "  &nbsp;·&nbsp;  ".join(parts) + "\n")


def inject(site, g, nb, path, solutions: bool) -> bool:
    doc = json.loads(path.read_text())
    cells = [c for c in doc["cells"]
             if TOP not in c.get("metadata", {}).get("tags", [])
             and BOTTOM not in c.get("metadata", {}).get("tags", [])]
    foot = solutions_bottom_cell(site, g, nb) if solutions else bottom_cell(site, g, nb)
    doc["cells"] = [top_cell(site, g, nb, solutions)] + cells + [foot]
    new = json.dumps(doc, indent=1) + "\n"
    if new == path.read_text():
        return False
    path.write_text(new)
    return True


def main() -> int:
    site, guides = load()
    changed = 0
    for g in guides:
        for nb in g.notebooks:
            if not nb.exists:
                continue
            for path, sol in ((nb.path, False), (nb.solutions, True)):
                if path.exists() and inject(site, g, nb, path, sol):
                    print(f"  navigation set: {path.relative_to(ROOT)}")
                    changed += 1
    print(f"  {changed} notebook(s) updated" if changed else "  navigation already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
