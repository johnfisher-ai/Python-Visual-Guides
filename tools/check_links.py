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

Two checks are for search engines. Every address in public/sitemap.xml has to resolve to a file
in public/ and be that page's canonical URL, and the sitemap has to list exactly the front page and
the guides that are not planned. Every page has to carry a canonical link to its own address and a
meta description, and none may carry noindex.
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


SITE = f"https://{OWNER}.github.io/{REPO}"


def canonical_of(name: str) -> str:
    return SITE + "/" + ("" if name == "index.html" else name)


def check_heads(pages) -> int:
    """Every page has its own canonical link and a description, and none says noindex.

    Files copied from tools/static/, such as the Search Console verification file, are not pages
    and are left out."""
    static = {f.name for f in (ROOT / "tools" / "static").iterdir() if f.is_file()}
    bad = 0
    for name, html in pages.items():
        if name in static:
            continue
        canon = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
        if canon != [canonical_of(name)]:
            print(f"  HEAD  {name}: canonical is {canon}, expected [{canonical_of(name)!r}]")
            bad += 1
        desc = re.findall(r'<meta name="description" content="([^"]*)"', html)
        if len(desc) != 1 or not desc[0].strip():
            print(f"  HEAD  {name}: needs exactly one non-empty meta description, found {desc}")
            bad += 1
        if re.search(r"noindex", html, re.I):
            print(f"  HEAD  {name}: carries noindex")
            bad += 1
    return bad


def check_sitemap(pages) -> int:
    """Every sitemap address resolves in public/, is that page's canonical, and the list is complete."""
    sys.path.insert(0, str(ROOT))
    from tools.build_sitemap import addresses
    sitemap = PUB / "sitemap.xml"
    if not sitemap.exists():
        print("  MISS  public/sitemap.xml does not exist")
        return 1
    bad = 0
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text())
    for loc in locs:
        local = as_local_path(loc)
        if local is None or not local.exists():
            print(f"  MISS  sitemap.xml -> {loc}  (no file in public/)")
            bad += 1
        elif canonical_of(local.name) != loc:
            print(f"  MISS  sitemap.xml -> {loc}  (the page's canonical is {canonical_of(local.name)})")
            bad += 1
    if locs != addresses():
        print(f"  MISS  sitemap.xml lists {len(locs)} pages; the manifest's published pages are {len(addresses())}")
        bad += 1
    print(f"  sitemap.xml: {len(locs)} addresses checked")
    return bad


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

    bad += check_heads(pages)
    bad += check_sitemap(pages)
    static = {f.name for f in (ROOT / "tools" / "static").iterdir() if f.is_file()}
    print(f"  {len(set(pages) - static)} pages: canonical link, description and no noindex checked")

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
