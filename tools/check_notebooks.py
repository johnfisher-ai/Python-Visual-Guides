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

MIN_IDEA_WORDS = 350

PARTS = [
    "What you will be able to do",
    # The idea comes before Setup on purpose: a reader should not meet a code
    # cell before anything has explained what the notebook is about.
    "The idea",
    "Setup",
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

    def section(part):
        """The cells under one heading, up to whatever part comes next.

        Derived from PARTS rather than written out, so reordering the shape
        does not silently leave a slice pointing the wrong way.
        """
        after = PARTS[PARTS.index(part) + 1:]
        end = min((idx[p] for p in after if p in idx), default=len(cs))
        return cs[idx[part] + 1: end]

    # Setup is exactly one code cell
    code_after_setup = [c for c in section("Setup") if c.get("cell_type") == "code"]
    if len(code_after_setup) != 1:
        problems.append((where, f"Setup has {len(code_after_setup)} code cells, expected 1"))

    # The idea, Worked examples and Common errors must show a reader something,
    # though not every cell need print: an assignment legitimately produces nothing.
    for part in ("The idea", "Worked examples", "Common errors"):
        run = [c for c in section(part)
               if c.get("cell_type") == "code" and src(c).strip()]
        if run and not any(c.get("outputs") for c in run):
            problems.append((where, f"no code cell under '{part}' has committed output, "
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
    """Catch cross-references that name a notebook which does not exist.

    References are written by title, not number, because numbers change: inserting
    Regular Expressions at position 5 shifted every notebook after it, and prose
    does not move with the manifest. A title is stable, and it is also what a
    reader remembers.

    A bolded phrase that looks like a title but matches nothing in the guide is
    almost always a renamed notebook or a typo, so it is reported. Bold is used
    for emphasis too, so only phrases that resemble a title are considered: the
    check looks for ones that differ from a real title by case or spacing.
    """
    titles = {nb.title for nb in guide.notebooks}
    folded = {t.lower(): t for t in titles}
    doc = json.loads(path.read_text())

    for cell in doc.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = src(cell)

        # a stale numeric reference, which this project no longer writes
        for m in re.finditer(r"\b[Nn]otebooks?\s+(\d+)\b", text):
            problems.append((path.relative_to(ROOT),
                             f"refers to {m.group(0)!r} by number. Use the notebook's "
                             f"title instead, because numbers shift when one is inserted"))

        # position by any other spelling is the same problem: "ten notebooks in",
        # "the last notebook", "six notebooks ago" all break when order changes.
        for pattern in (
            r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
            r"\s+notebooks?\b",
            r"\bthe (?:last|previous|preceding|next|following|first) (?:notebook|guide)\b",
            r"\bnotebooks?\s+(?:ago|back|earlier|later)\b",
            r"\b(?:first|second|third|fourth|fifth) notebook\b",
        ):
            for m in re.finditer(pattern, text, re.I):
                problems.append((path.relative_to(ROOT),
                                 f"{m.group(0)!r} describes a notebook by position, which "
                                 f"breaks when one is inserted or moved. Name it instead"))

        # a bolded phrase that is nearly a title but does not match one
        for m in re.finditer(r"\*\*([A-Z][A-Za-z][A-Za-z ,'-]{2,40})\*\*", text):
            phrase = m.group(1).strip()
            if phrase in titles:
                continue
            near = folded.get(phrase.lower())
            if near:
                problems.append((path.relative_to(ROOT),
                                 f"names {phrase!r}, but the notebook is titled {near!r}"))


def executable(path: Path, problems: list) -> None:
    """Catch what would fail the notebooks workflow, which runs without --allow-errors.

    A cell whose committed output is an error must carry the raises-exception tag,
    or nbconvert stops there and the notebook "did not run top to bottom". Running
    a notebook locally with --allow-errors hides this, so it has to be checked here.

    nbformat 4.5 also requires an id on every cell, which is a hard error in later
    versions of nbformat.
    """
    doc = json.loads(path.read_text())
    for i, cell in enumerate(doc.get("cells", [])):
        if "id" not in cell:
            problems.append((path.relative_to(ROOT),
                             f"cell {i} has no id, which nbformat 4.5 requires"))
        if cell.get("cell_type") != "code":
            continue
        errored = any(o.get("output_type") == "error" for o in cell.get("outputs", []))
        tagged = "raises-exception" in cell.get("metadata", {}).get("tags", [])
        if errored and not tagged:
            name = next((o.get("ename") for o in cell["outputs"]
                         if o.get("output_type") == "error"), "an error")
            problems.append((path.relative_to(ROOT),
                             f"cell {i} shows {name} but is not tagged raises-exception, "
                             f"so the workflow will stop there"))
        elif tagged and not errored:
            problems.append((path.relative_to(ROOT),
                             f"cell {i} is tagged raises-exception but raises nothing"))


def orientation(path: Path, problems: list) -> None:
    """The idea must orient the reader before it shows any code.

    A definition followed straight away by a code cell teaches syntax and
    nothing else. The reader needs to know what problem the thing solves and
    where they will meet it before they are asked to run anything.

    This counts words, which is a floor and not a measure of quality. Clearing
    it proves only that prose is present.
    """
    doc = json.loads(path.read_text())
    cells = doc.get("cells", [])
    start = next((i for i, c in enumerate(cells)
                  if src(c).lstrip().startswith("## The idea")), None)
    if start is None:
        return                       # the missing-heading case is already reported
    first_code = next((i for i in range(start, len(cells))
                       if cells[i].get("cell_type") == "code"), None)
    if first_code is None:
        return
    words = sum(len(src(cells[i]).split()) for i in range(start, first_code))
    if words < MIN_IDEA_WORDS:
        problems.append((path.relative_to(ROOT),
                         f"'The idea' gives {words} words before its first code cell, "
                         f"under the {MIN_IDEA_WORDS} minimum. Say what problem this "
                         f"solves and where the reader will meet it, then show code"))


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
            executable(nb.path, problems)
            orientation(nb.path, problems)
            checked += 1
            # A solutions notebook is read on its own, so it needs navigation too.
            # It is exempt from the eight-part shape, which is for teaching notebooks.
            if nb.solutions.exists():
                doc = json.loads(nb.solutions.read_text())
                tags = [t for c in doc.get("cells", [])
                        for t in c.get("metadata", {}).get("tags", [])]
                executable(nb.solutions, problems)
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
