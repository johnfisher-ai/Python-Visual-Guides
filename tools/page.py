"""The shared page shell: head, masthead, nav, footer.

Every page is generated. Editing public/*.html by hand loses the change on the
next build.
"""

from html import escape as esc
from pathlib import Path

SITE = "https://johnfisher-ai.github.io/Python-Visual-Guides"
REPO = "https://github.com/johnfisher-ai/Python-Visual-Guides"
PUBLIC = Path(__file__).resolve().parent.parent / "public"

# Nav order. A page appears only once it exists, so the nav never offers a 404.
COLAB = "https://colab.research.google.com/github/johnfisher-ai/Python-Visual-Guides/blob/main/"
RAW = f"{REPO}/blob/main/"


def _sequence():
    """Reading order for the previous/next pager: the library, then every guide."""
    from tools.manifest import load
    _site, guides = load()
    return [("./", "index.html", "The guides")] + [
        (g.page, g.page, g.title) for g in guides
    ]


# The pager walks every guide in order.
PAGES = _sequence()

# The nav stays short. Eleven guides across the top would wrap to three lines and
# tell a reader nothing; the library page lists them properly.
NAV = [("./", "index.html", "The guides")]

EXTRA_NAV = [
    (REPO, "Repository"),
]


def _nav(current: str) -> str:
    out = ['<nav class="site"><div class="wrap">']
    for href, filename, label in NAV:
        if filename != current and not (PUBLIC / filename).exists():
            continue
        aria = ' aria-current="page"' if filename == current else ""
        out.append(f'<a href="{href}"{aria}>{esc(label)}</a>')
    for href, label in EXTRA_NAV:
        out.append(f'<a href="{href}">{esc(label)}</a>')
    out.append("</div></nav>")
    return "".join(out)


def head(*, filename, title, tab_title, description, card_title, card_desc, kicker, byline):
    canonical = SITE + "/" + ("" if filename == "index.html" else filename)
    img = f"{SITE}/assets/img/social-card.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(tab_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="author" content="John Fisher">
<meta name="theme-color" content="#2f5d94">
<meta property="og:type" content="website">
<meta property="og:site_name" content="A Config-Driven Agent Network">
<meta property="og:title" content="{esc(card_title)}">
<meta property="og:description" content="{esc(card_desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="627">
<meta property="og:image:alt" content="A broker agent fanning out to five specialist agents, with a human approval gate on the risky path.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(card_title)}">
<meta name="twitter:description" content="{esc(card_desc)}">
<meta name="twitter:image" content="{img}">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>

<header class="top">
  <div class="wrap">
    <p class="kicker">{esc(kicker)}</p>
    <h1>{esc(title)}</h1>
    <p class="byline">{byline}</p>
  </div>
</header>

{_nav(filename)}

<main>
<div class="wrap">
"""


def _pager(current: str) -> str:
    """Previous and next through the four pages, in reading order."""
    seq = [(href, fn, label) for href, fn, label in PAGES if (PUBLIC / fn).exists()]
    idx = next((i for i, (_, fn, _) in enumerate(seq) if fn == current), None)
    if idx is None:
        return ""
    out = ['<nav class="pager">']
    if idx > 0:
        href, _, label = seq[idx - 1]
        out.append(f'<a class="prev" href="{href}"><span>Previous</span><b>{esc(label)}</b></a>')
    else:
        out.append("<span></span>")
    if idx < len(seq) - 1:
        href, _, label = seq[idx + 1]
        out.append(f'<a class="next" href="{href}"><span>Next</span><b>{esc(label)}</b></a>')
    else:
        out.append("<span></span>")
    out.append("</nav>")
    return "".join(out)


def foot(filename: str = ""):
    return f"""
</div>
</main>

<footer class="site">
  <div class="wrap">
    {_pager(filename)}
    <p class="sig">Built by John Fisher. Code under the MIT license.</p>
  </div>
</footer>

</body>
</html>
"""


def write(filename: str, body: str) -> None:
    (PUBLIC / filename).write_text(body)
    print(f"  wrote public/{filename}  ({len(body):,} bytes)")
