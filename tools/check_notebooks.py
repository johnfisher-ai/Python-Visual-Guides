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


def main() -> int:
    _site, guides = load()
    problems: list = []
    checked = 0
    for g in guides:
        for nb in g.notebooks:
            if nb.exists:
                check(nb.path, problems)
                checked += 1

    if not checked:
        print("  no notebooks written yet, nothing to check")
        return 0

    print(f"  {checked} notebook(s) checked")
    for where, why in problems:
        print(f"  BAD   {where}: {why}")
    print("  every notebook has the eight-part shape" if not problems
          else f"  *** {len(problems)} problem(s) ***")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
