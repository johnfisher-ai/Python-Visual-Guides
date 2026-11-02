"""Copy every file in tools/static/ (apart from its README) into public/, unchanged.

The Google Search Console verification file is kept there, so each build puts it back in public/ and it
is served at the site's root. Nothing in public/ is ever deleted here.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "tools" / "static"
PUBLIC = ROOT / "public"


def main() -> int:
    copied = []
    for src in sorted(STATIC.iterdir()):
        if src.is_file() and src.name != "README.md":
            shutil.copyfile(src, PUBLIC / src.name)
            copied.append(src.name)
    print(f"  {len(copied)} static file(s) copied into public/: {', '.join(copied) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
