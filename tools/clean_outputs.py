"""Tidy the printed output of notebooks, as part of the build.

A notebook line that starts with `!` runs a shell command inside a pseudo-terminal, so what
it prints arrives the way a terminal would receive it: every line ends in a carriage return
and a line feed, and tools that detect a terminal add escape codes for bold and color. curl
bolds header names, and Python 3.14's json.tool colors its output where Colab's 3.12 does
not. Jupyter and Colab hide both, but they are still in the committed file, where an HTML
rendering can show every line followed by an empty one, and where the escape codes record
the machine that ran the notebook rather than what a reader will see.

Printed text can also be saved in pieces. The kernel sends what a cell prints in batches, and
when a batch ends partway through a print, the rest of that print is saved as an output of its
own. A renderer that draws each output as its own block then shows one printed line as two, as
happened to a line in Headers and Content Types. This merges adjacent outputs of the same stream
back into one.

This rewrites stream output only, in the JSON layout the notebook already has, and leaves
tracebacks with their color codes, which every notebook renderer draws. check_notebooks.py
fails on any stream output this has not tidied.
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


def joined(text) -> str:
    return text if isinstance(text, str) else "".join(text)


def tidy(outputs: list) -> list:
    """The outputs with adjacent pieces of one stream merged, and terminal characters removed."""
    tidied = []
    for out in outputs:
        if out.get("output_type") != "stream":
            tidied.append(out)
            continue
        previous = tidied[-1] if tidied else {}
        if previous.get("output_type") == "stream" and previous.get("name") == out.get("name"):
            text = clean(joined(previous["text"]) + joined(out["text"]))
            previous["text"] = text if isinstance(previous["text"], str) else text.splitlines(keepends=True)
            continue
        text = clean(joined(out["text"]))
        tidied.append({**out, "text": text if isinstance(out["text"], str) else text.splitlines(keepends=True)})
    return tidied


def dumps_like(original: str, doc: dict) -> str:
    """doc as JSON, laid out as the file it came from was: by inject_nav, or by nbformat."""
    parsed = json.loads(original)
    for sort_keys, ensure_ascii in [(False, True), (True, False), (False, False), (True, True)]:
        if json.dumps(parsed, indent=1, sort_keys=sort_keys, ensure_ascii=ensure_ascii) + "\n" == original:
            return json.dumps(doc, indent=1, sort_keys=sort_keys, ensure_ascii=ensure_ascii) + "\n"
    return json.dumps(doc, indent=1) + "\n"


def main() -> int:
    rewritten = []
    for path in sorted(NOTEBOOKS.rglob("*.ipynb")):
        original = path.read_text()
        doc = json.loads(original)
        changed = False
        for cell in doc.get("cells", []):
            if "outputs" in cell:
                outputs = tidy(cell["outputs"])
                if outputs != cell["outputs"]:
                    cell["outputs"] = outputs
                    changed = True
        if changed:
            path.write_text(dumps_like(original, doc))
            rewritten.append(path.relative_to(ROOT))
    for p in rewritten:
        print(f"  tidied {p}")
    print(f"  {len(rewritten)} notebook(s) had terminal characters or printed output in pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
