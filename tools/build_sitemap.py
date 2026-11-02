"""Write public/sitemap.xml from the manifest: the front page and every guide that is not planned.

Each address is the page's canonical URL, the one tools/page.py writes into its <link rel="canonical">,
so a search engine sees one address per page. A planned guide has a page that says the guide is coming,
and it stays out of the sitemap until its status changes. check_links.py checks that every address
resolves to a file in public/, matches that file's canonical link, and that no published guide is missing.
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import page                                          # noqa: E402
from tools.manifest import load                                 # noqa: E402


def addresses() -> list[str]:
    _, guides = load()
    return [page.SITE + "/"] + [f"{page.SITE}/{g.page}" for g in guides if g.status != "planned"]


def main() -> int:
    urls = addresses()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f"  <url><loc>{escape(url)}</loc></url>" for url in urls]
    lines.append("</urlset>")
    (page.PUBLIC / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  public/sitemap.xml lists {len(urls)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
