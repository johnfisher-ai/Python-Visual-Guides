"""Read and validate manifest.json.

The manifest is the source of truth for what exists and in what order. Every page,
every nav and every checker reads it, so a mistake here is a mistake everywhere,
which is why it validates rather than merely loading.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
NOTEBOOKS = ROOT / "notebooks"

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Notebook:
    n: int
    slug: str
    title: str
    blurb: str
    guide: str

    @property
    def filename(self) -> str:
        return f"{self.n:02d}-{self.slug}.ipynb"

    @property
    def path(self) -> Path:
        return NOTEBOOKS / self.guide / self.filename

    @property
    def solutions(self) -> Path:
        return NOTEBOOKS / self.guide / f"{self.n:02d}-{self.slug}-solutions.ipynb"

    @property
    def exists(self) -> bool:
        return self.path.exists()


@dataclass
class Guide:
    slug: str
    number: int
    band: str
    title: str
    subtitle: str
    status: str
    intro: str
    prerequisites: str
    notebooks: list[Notebook]
    credits: str = ""

    @property
    def page(self) -> str:
        return f"{self.slug}.html"

    @property
    def written(self) -> int:
        return sum(1 for nb in self.notebooks if nb.exists)


def load() -> tuple[dict, list[Guide]]:
    raw = json.loads(MANIFEST.read_text())
    guides = []
    for g in raw["guides"]:
        nbs = [Notebook(n=nb["n"], slug=nb["slug"], title=nb["title"],
                        blurb=nb["blurb"], guide=g["slug"])
               for nb in g["notebooks"]]
        guides.append(Guide(
            slug=g["slug"], number=g["number"], band=g["band"], title=g["title"],
            subtitle=g["subtitle"], status=g["status"], intro=g["intro"],
            prerequisites=g["prerequisites"], notebooks=nbs,
            credits=g.get("credits", "")))
    return raw["site"], sorted(guides, key=lambda g: g.number)


def validate() -> int:
    """Report anything that would make the generated pages lie."""
    site, guides = load()
    bad = []

    numbers = [g.number for g in guides]
    if numbers != list(range(1, len(guides) + 1)):
        bad.append(f"guide numbers are {numbers}, expected 1..{len(guides)}")
    if len({g.slug for g in guides}) != len(guides):
        bad.append("duplicate guide slug")

    for g in guides:
        if not SLUG.match(g.slug):
            bad.append(f"{g.slug}: not a clean slug")
        if g.status not in ("building", "planned", "published"):
            bad.append(f"{g.slug}: unknown status {g.status!r}")
        ns = [nb.n for nb in g.notebooks]
        if ns != list(range(1, len(ns) + 1)):
            bad.append(f"{g.slug}: notebook numbers are {ns}, expected 1..{len(ns)}")
        for nb in g.notebooks:
            if not SLUG.match(nb.slug):
                bad.append(f"{g.slug}/{nb.n}: not a clean slug: {nb.slug!r}")
            if not nb.blurb.strip():
                bad.append(f"{g.slug}/{nb.n}: empty blurb")

        # a notebook on disk that the manifest does not know about is invisible
        d = NOTEBOOKS / g.slug
        if d.is_dir():
            known = {nb.filename for nb in g.notebooks}
            known |= {nb.solutions.name for nb in g.notebooks}
            for f in sorted(d.glob("*.ipynb")):
                if f.name not in known:
                    bad.append(f"{g.slug}: {f.name} is on disk but not in the manifest")

    total = sum(len(g.notebooks) for g in guides)
    written = sum(g.written for g in guides)
    print(f"  {len(guides)} guides, {total} notebooks planned, {written} written")
    for b in bad:
        print(f"  BAD   {b}")
    print("  manifest is consistent" if not bad else f"  *** {len(bad)} problem(s) ***")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(validate())
