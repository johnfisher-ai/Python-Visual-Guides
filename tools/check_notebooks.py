#!/usr/bin/env python3
"""Check every notebook has the eight-part shape, and that it is honest.

The notebook is the product, so its structure is worth enforcing rather than
remembering. Each rule below is a failure that has a cost for the reader:

  headings      a reader relies on the same shape in every notebook
  setup cell    part 2 must be exactly one code cell, so it can be run first
  outputs       a reader on GitHub sees only what was committed
  empty tasks   it is very easy to solve your own exercise while testing it,
                save the notebook, and ship the answer inside the question
  solutions     every notebook needs its companion
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.manifest import load                                  # noqa: E402

PARTS = [
    "What you will be able to do",
    "Setup",
    "The idea",
    "Worked examples",
    "Your turn",
    "Common errors",
    "Recap",
    "What is next",
]
HEAD = re.compile(r"^##\s+(.+?)\s*$", re.M)


def cells(nb: dict):
    return nb.get("cells", [])


def src(cell) -> str:
    s = cell.get("source", "")
    return s if isinstance(s, str) else "".join(s)


def check(path: Path, problems: list) -> None:
    where = path.relative_to(ROOT)
    try:
        nb = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        problems.append((where, f"will not parse: {exc}"))
        return

    cs = cells(nb)

    # A notebook opened in Colab has no site around it. Without these a reader has
    # no way back to the guide and no way on to the next notebook.
    tags = [t for c in cs for t in c.get("metadata", {}).get("tags", [])]
    if "nav-top" not in tags or "nav-bottom" not in tags:
        problems.append((where, "no navigation cells. Run tools/inject_nav.py"))

    md = [(i, src(c)) for i, c in enumerate(cs) if c.get("cell_type") == "markdown"]
    found = [(i, h) for i, text in md for h in HEAD.findall(text)]
    order = [h for _, h in found if h in PARTS]

    missing = [p for p in PARTS if p not in order]
    if missing:
        problems.append((where, f"missing heading(s): {', '.join(missing)}"))
        return
    if order != PARTS:
        problems.append((where, f"headings out of order: {' / '.join(order)}"))
    for p in PARTS:
        if order.count(p) > 1:
            problems.append((where, f"heading appears {order.count(p)} times: {p}"))

    idx = {h: i for i, h in found if h in PARTS}

    # part 2 is exactly one code cell
    after_setup = [c for c in cs[idx["Setup"] + 1: idx["The idea"]]]
    code_after_setup = [c for c in after_setup if c.get("cell_type") == "code"]
    if len(code_after_setup) != 1:
        problems.append((where, f"Setup has {len(code_after_setup)} code cells, expected 1"))

    # parts 3, 4 and 6 must show a reader something, though not every cell need
    # print: an assignment legitimately produces nothing.
    for a, b in (("The idea", "Worked examples"),
                 ("Worked examples", "Your turn"),
                 ("Common errors", "Recap")):
        run = [c for c in cs[idx[a] + 1: idx[b]]
               if c.get("cell_type") == "code" and src(c).strip()]
        if run and not any(c.get("outputs") for c in run):
            problems.append((where, f"no code cell under '{a}' has committed output, "
                                    f"so a reader on GitHub sees no results there"))

    # part 5 must contain no solved code
    for c in cs[idx["Your turn"] + 1: idx["Common errors"]]:
        if c.get("cell_type") != "code":
            continue
        body = [ln for ln in src(c).splitlines()
                if ln.strip() and not ln.strip().startswith("#")]
        if body:
            problems.append((where, "an exercise cell contains code, not just a comment. "
                                    "Did you leave your own solution in?"))
            break

    if "-solutions" not in path.name:
        sol = path.with_name(path.name.replace(".ipynb", "-solutions.ipynb"))
        if not sol.exists():
            problems.append((where, f"no solutions notebook at {sol.name}"))
        else:
            # Promising a solutions notebook without linking it leaves the reader
            # hunting for a file they have no way to find.
            turn = "".join(src(c) for c in cs[idx["Your turn"]: idx["Common errors"]]
                           if c.get("cell_type") == "markdown")
            if sol.name not in turn:
                problems.append((where, "the 'Your turn' section does not link "
                                        f"{sol.name}, so a reader cannot reach it"))


def cross_refs(path: Path, guide, problems: list) -> None:
    """Catch cross-references left stale by a renumbering.

    Prose says things like "notebook 7 returns to it" or "**Notebook 3, Numbers**".
    Inserting a notebook shifts every number after it, and the prose does not move
    with the manifest. A number past the end of the guide is always wrong. A number
    followed by a title that belongs to a different notebook is always wrong too,
    and that is the case a renumbering actually produces.
    """
    titles = {nb.n: nb.title for nb in guide.notebooks}
    doc = json.loads(path.read_text())
    for cell in doc.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = src(cell)
        for m in re.finditer(r"[Nn]otebooks?\s+(\d+)(,\s*([A-Z][A-Za-z ]+?))?(?=\*\*|,|\.|;|:|\)|$)",
                             text):
            n, named = int(m.group(1)), (m.group(3) or "").strip()
            if n not in titles:
                problems.append((path.relative_to(ROOT),
                                 f"points at notebook {n}, which this guide does not have"))
            elif named and named != titles[n]:
                problems.append((path.relative_to(ROOT),
                                 f"calls notebook {n} '{named}', the manifest says "
                                 f"'{titles[n]}'"))


def main() -> int:
    _site, guides = load()
    problems: list = []
    checked = 0
    for g in guides:
        for nb in g.notebooks:
            if not nb.exists:
                continue
            check(nb.path, problems)
            cross_refs(nb.path, g, problems)
            checked += 1
            # A solutions notebook is read on its own, so it needs navigation too.
            # It is exempt from the eight-part shape, which is for teaching notebooks.
            if nb.solutions.exists():
                doc = json.loads(nb.solutions.read_text())
                tags = [t for c in doc.get("cells", [])
                        for t in c.get("metadata", {}).get("tags", [])]
                if "nav-top" not in tags or "nav-bottom" not in tags:
                    problems.append((nb.solutions.relative_to(ROOT),
                                     "no navigation cells. Run tools/inject_nav.py"))
                checked += 1

    if not checked:
        print("  no notebooks written yet, nothing to check")
        return 0

    print(f"  {checked} notebook(s) checked")
    for where, why in problems:
        print(f"  BAD   {where}: {why}")
    print("  every notebook has the shape, and its cross-references resolve"
          if not problems
          else f"  *** {len(problems)} problem(s) ***")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
