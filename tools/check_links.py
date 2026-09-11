"""Resolve every link in public/ and in the notebooks, and report anything that does not exist.

Three kinds get checked, and the third is the one a human will never catch:

  relative      href="assets/css/site.css"   resolved against the page it is on
  anchors       href="page.html#section"     the id has to exist in that page
  self-links    Colab, github.com/blob, raw.githubusercontent.com and Pages URLs
                encode a path inside this repository, so they are checked against
                the local tree with no network call. A dead Colab button is
                invisible otherwise: the page loads, and the notebook 404s only
                when a reader clicks it.

Self-links inside notebooks are checked too. The one that matters most is a file
a Setup cell downloads when it runs in Colab: CI runs beside the file and never
downloads it, so a wrong path there passes every run and fails every reader.
Keep such a URL in one string literal, or only its first half is seen.

A bare "#frag" targets the page it appears on, not index.html. Getting that
wrong reports a false failure on any in-page anchor.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
NOTEBOOKS = ROOT / "notebooks"

OWNER, REPO = "johnfisher-ai", "Python-Visual-Guides"

# URLs that point back into this repository. Checked against the checkout,
# because a path that is wrong here is wrong for every reader.
# (pattern, base) pairs. A github.com or Colab URL names a path in the repository.
# A Pages URL names a path on the SITE, and this workflow publishes public/, so the
# two resolve against different roots. Getting that wrong reports the site's own
# home page as missing.
SELF = [
    (re.compile(rf"^https://colab\.research\.google\.com/github/{OWNER}/{REPO}/blob/[^/]+/(.+)$"), "repo"),
    (re.compile(rf"^https://github\.com/{OWNER}/{REPO}/(?:blob|raw)/[^/]+/(.+)$"), "repo"),
    (re.compile(rf"^https://raw\.githubusercontent\.com/{OWNER}/{REPO}/[^/]+/(.+)$"), "repo"),
    (re.compile(rf"^https://{OWNER}\.github\.io/{REPO}/(.*)$"), "site"),
]

# A URL in markdown or in code. It stops at whitespace, quotes, brackets and
# backticks; punctuation that ends the sentence around it is trimmed off after.
URL = re.compile(r"https?://[^\s\"'<>()\[\]`]+")


def as_local_path(url: str):
    """A URL pointing back at this project, as a local Path, else None."""
    for pat, base in SELF:
        m = pat.match(url)
        if m:
            rel = unquote(m.group(1).split("#")[0].split("?")[0]) or "index.html"
            if base == "site" and rel.endswith("/"):
                rel += "index.html"
            return (ROOT if base == "repo" else PUB) / rel
    return None


def notebook_links():
    """Every URL in every notebook cell, as (notebook, url) pairs."""
    for nb in sorted(NOTEBOOKS.rglob("*.ipynb")):
        for cell in json.loads(nb.read_text()).get("cells", []):
            source = cell.get("source", "")
            text = source if isinstance(source, str) else "".join(source)
            for url in URL.findall(text):
                yield nb, url.rstrip(".,;:*")


def main() -> int:
    bad = 0
    pages = {p.name: p.read_text() for p in sorted(PUB.glob("*.html"))}
    for name, html in pages.items():
        for href in sorted(set(re.findall(r'(?:href|src)="([^"]+)"', html))):
            local = as_local_path(href)
            if local is not None:
                if not local.exists():
                    rel = local.relative_to(ROOT) if ROOT in local.parents else local
                    print(f"  MISS  {name} -> {href}  (no {rel})")
                    bad += 1
                continue
            if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
                continue
            base, _, frag = href.partition("#")
            if base in ("", "./"):
                target = name if not base else "index.html"
            else:
                target = base
            if target not in pages:
                if not (PUB / target).exists():
                    print(f"  MISS  {name} -> {href}  (no such file)")
                    bad += 1
                continue
            if frag and f'id="{frag}"' not in pages[target]:
                print(f"  MISS  {name} -> {href}  (no such anchor)")
                bad += 1

    checked = 0
    for nb, url in notebook_links():
        local = as_local_path(url)
        if local is None:
            continue
        checked += 1
        if not local.exists():
            print(f"  MISS  {nb.relative_to(ROOT)} -> {url}  (no {local.relative_to(ROOT)})")
            bad += 1
    print(f"  {checked} self-links in notebooks checked")
    print(f"  {'all links and anchors resolve' if not bad else f'*** {bad} broken ***'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
