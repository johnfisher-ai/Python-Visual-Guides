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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import page                                   # noqa: E402

PUB = ROOT / "public"

# Strings that must appear on every page. Reference page.py constants, never
# literals: a literal here is a second copy that will drift.
#     REQUIRED = [("the data notice", page.DATA_NOTICE)]
REQUIRED: list[tuple[str, str]] = []

# Words that must never reach a reader, with the reason shown on failure.
BANNED = [
    (r"—", "prose em-dash"),
    (r"\b(licence|colour|behaviour|organis\w+)\b", "British spelling"),
    (r"\b(in the original|the original (?:version|implementation|code)"
     r"|the first version|an earlier version|used to be|was broken)\b",
     "describes an earlier version instead of the current one"),
    (r"\b(lorem ipsum|TODO|FIXME|XXX)\b", "placeholder left in"),
]


def strip(markup: str) -> str:
    """Tag-stripped, entity-decoded, whitespace-collapsed."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def visible(p: Path) -> str:
    """What a reader sees, with quoted source excluded."""
    h = re.sub(r"<pre.*?</pre>|<details.*?</details>", " ", p.read_text(), flags=re.S)
    return strip(h)


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
        for pattern, reason in BANNED:
            for m in set(re.findall(pattern, text, re.I)):
                hit = m if isinstance(m, str) else m[0]
                print(f"  BAD   {f.name}: {hit!r} ({reason})")
                bad += 1

    print(f"  {'content checks pass' if not bad else f'*** {bad} problem(s) ***'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
