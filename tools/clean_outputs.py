"""Strip terminal control characters from notebook output, as part of the build.

A notebook line that starts with `!` runs a shell command inside a pseudo-terminal, so what
it prints arrives the way a terminal would receive it: every line ends in a carriage return
and a line feed, and tools that detect a terminal add escape codes for bold and color. curl
bolds header names, and Python 3.14's json.tool colors its output where Colab's 3.12 does
not. Jupyter and Colab hide both, but they are still in the committed file, where an HTML
rendering can show every line followed by an empty one, and where the escape codes record
the machine that ran the notebook rather than what a reader will see.

This rewrites stream output only, and only those characters. Tracebacks keep their color
codes, which every notebook renderer draws. check_notebooks.py fails on any stream output
this has not cleaned.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"

ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")      # bold, color and reset codes
LINE_END = re.compile(r"\r+\n")                     # a terminal's \r\n, and curl's \r\r\n


def clean(text: str) -> str:
    return LINE_END.sub("\n", ESCAPE.sub("", text)).rstrip("\r")


def main() -> int:
    cleaned = []
    for path in sorted(NOTEBOOKS.rglob("*.ipynb")):
        doc = json.loads(path.read_text())
        changed = False
        for cell in doc.get("cells", []):
            for out in cell.get("outputs", []):
                if out.get("output_type") != "stream":
                    continue
                text = out["text"] if isinstance(out["text"], str) else "".join(out["text"])
                new = clean(text)
                if new != text:
                    out["text"] = new if isinstance(out["text"], str) else new.splitlines(keepends=True)
                    changed = True
        if changed:
            path.write_text(json.dumps(doc, indent=1) + "\n")    # the format inject_nav writes
            cleaned.append(path.relative_to(ROOT))
    for p in cleaned:
        print(f"  cleaned {p}")
    print(f"  {len(cleaned)} notebook(s) had terminal characters in their output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
