"""Keep the guide table in README.md in step with the manifest.

The README is hand-written except for the table of guides, which sits between two marker
comments and is rewritten on every build, so a guide's status and notebook count change in
manifest.json and nowhere else. Written by hand, the table went stale as soon as the first
guide changed status.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.manifest import load                                 # noqa: E402
from tools.build_guide import STATUS                            # noqa: E402

README = ROOT / "README.md"
START = ("<!-- guide-table: generated from manifest.json by tools/build_readme.py; "
         "edit the manifest, not this table -->")
END = "<!-- /guide-table -->"


def table(guides):
    rows = ["| | Guide | Notebooks | |", "|---|---|---|---|"]
    for g in guides:
        title = f"**{g.title}**" if g.status == "building" else g.title   # the one being written
        rows.append(f"| {g.number} | {title} | {len(g.notebooks)} | {STATUS[g.status][0]} |")
    return "\n".join(rows)


def build():
    _, guides = load()
    text = README.read_text()
    head, start, rest = text.partition(START)
    _, end, tail = rest.partition(END)
    if not (start and end):
        sys.exit("README.md has lost its guide-table markers. Put these two lines back "
                 f"around the table:\n  {START}\n  {END}")
    new = f"{head}{START}\n\n{table(guides)}\n\n{END}{tail}"
    if new == text:
        print("  README.md guide table: already current")
    else:
        README.write_text(new)
        print("  README.md guide table: rewritten from the manifest")


if __name__ == "__main__":
    build()
