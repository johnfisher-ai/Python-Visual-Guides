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


def colab(guide_slug: str, filename: str) -> str:
    return page.COLAB + f"notebooks/{guide_slug}/{filename}"


def guide_url(g) -> str:
    return f"{page.SITE}/{g.page}"


def cell(tag: str, text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {"tags": [tag]},
            "source": text.strip("\n") + "\n"}


def top_cell(site, g, nb) -> dict:
    return cell(TOP, f"""
[{site['title']}]({page.SITE}/) &nbsp;&rsaquo;&nbsp; [{g.title}]({guide_url(g)})

# {nb.title}
""")


def bottom_cell(site, g, nb) -> dict:
    prev_nb = next((x for x in g.notebooks if x.n == nb.n - 1), None)
    next_nb = next((x for x in g.notebooks if x.n == nb.n + 1), None)

    left = (f"&#8592; **Previous:** [{prev_nb.title}]({colab(g.slug, prev_nb.filename)})"
            if prev_nb and prev_nb.exists else "")
    right = (f"**Next:** [{next_nb.title}]({colab(g.slug, next_nb.filename)}) &#8594;"
             if next_nb and next_nb.exists else "")
    middle = f"[{g.title} Notebooks]({guide_url(g)})"

    parts = [p for p in (left, middle, right) if p]
    return cell(BOTTOM, "---\n\n" + "  &nbsp;·&nbsp;  ".join(parts) + "\n")


def inject(site, g, nb) -> bool:
    doc = json.loads(nb.path.read_text())
    cells = [c for c in doc["cells"]
             if TOP not in c.get("metadata", {}).get("tags", [])
             and BOTTOM not in c.get("metadata", {}).get("tags", [])]
    doc["cells"] = [top_cell(site, g, nb)] + cells + [bottom_cell(site, g, nb)]
    new = json.dumps(doc, indent=1) + "\n"
    if new == nb.path.read_text():
        return False
    nb.path.write_text(new)
    return True


def main() -> int:
    site, guides = load()
    changed = 0
    for g in guides:
        for nb in g.notebooks:
            if nb.exists and inject(site, g, nb):
                print(f"  navigation set: {nb.path.relative_to(ROOT)}")
                changed += 1
    print(f"  {changed} notebook(s) updated" if changed else "  navigation already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
