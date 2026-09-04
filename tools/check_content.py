"""Assert the house rules against rendered text, as part of the build.

Written because ad-hoc greps kept giving false results: HTML entities, an
apostrophe written literally where the check expected &#x27;, and a bare
"#frag" resolved against the wrong file. Every check here runs against
tag-stripped, entity-decoded text, which is what a reader actually sees.

Add project rules to REQUIRED and BANNED. A claim that must appear on every
page belongs in REQUIRED, as a constant in page.py so the pages and the check
cannot drift apart.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import page                                   # noqa: E402

PUB = ROOT / "public"
NOTEBOOKS = ROOT / "notebooks"

# Strings that must appear on every page. Reference page.py constants, never
# literals: a literal here is a second copy that will drift.
#     REQUIRED = [("the data notice", page.DATA_NOTICE)]
REQUIRED: list[tuple[str, str]] = []

# Words that must never reach a reader, with the reason shown on failure.
BANNED = [
    (r"—", "prose em-dash"),
    # An explicit list, not a pattern: "-ise" as a rule would flag rise, precise,
    # promise, advise, exercise. "Analysis" is correct in American English too.
    (r"\b(licence|colour|colours|behaviour|behaviours|favourite|neighbour|neighbours"
     r"|centre|defence|grey|whilst|amongst|practise"
     r"|organis\w+|recognis\w+|memoris\w+|capitalis\w+|normalis\w+|visualis\w+"
     r"|optimis\w+|vectoris\w+|summaris\w+|realis\w+|initialis\w+|analyse\w*"
     r"|labelled|labelling|modelled|modelling|travelled|cancelled)\b", "British spelling"),
    (r"\b(lorem ipsum|TODO|FIXME|XXX)\b", "placeholder left in"),
]

# Rules for the pages only. This one exists because documentation kept narrating
# what an earlier version did; in a notebook, "what `apples` used to be" is
# ordinary teaching prose about a value, not a description of old code.
PAGE_ONLY = [
    (r"\b(in the original|the original (?:version|implementation|code)"
     r"|the first version|an earlier version|used to be|was broken)\b",
     "describes an earlier version instead of the current one"),
]


def strip(markup: str) -> str:
    """Tag-stripped, entity-decoded, whitespace-collapsed."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def visible(p: Path) -> str:
    """What a reader sees, with quoted source excluded."""
    h = re.sub(r"<pre.*?</pre>|<details.*?</details>", " ", p.read_text(), flags=re.S)
    return strip(h)


def prose(nb_path: Path) -> str:
    """The markdown a reader reads, with code spans and fenced blocks removed.

    Notebooks hold far more prose than the pages do, so the house rules have to
    reach them. Code is excluded because a word being *discussed* in backticks
    is not the same as a word being used.
    """
    doc = json.loads(nb_path.read_text())
    out = []
    for cell in doc.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = "".join(cell["source"])
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        text = re.sub(r"`[^`]*`", " ", text)
        out.append(text)
    return " ".join(" ".join(out).split())


def main() -> int:
    pages = sorted(PUB.glob("*.html"))
    if not pages:
        print("  no pages in public/, nothing to check")
        return 0

    bad = 0
    for f in pages:
        text = visible(f)
        for label, needle in REQUIRED:
            if strip(needle) not in text:
                print(f"  MISS  {f.name}: {label} absent")
                bad += 1
        for pattern, reason in BANNED + PAGE_ONLY:
            for m in set(re.findall(pattern, text, re.I)):
                hit = m if isinstance(m, str) else m[0]
                print(f"  BAD   {f.name}: {hit!r} ({reason})")
                bad += 1

    for f in sorted(NOTEBOOKS.rglob("*.ipynb")):
        text = prose(f)
        for pattern, reason in BANNED:
            for m in set(re.findall(pattern, text, re.I)):
                hit = m if isinstance(m, str) else m[0]
                print(f"  BAD   {f.relative_to(ROOT)}: {hit!r} ({reason})")
                bad += 1

    print(f"  {'content checks pass' if not bad else f'*** {bad} problem(s) ***'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
