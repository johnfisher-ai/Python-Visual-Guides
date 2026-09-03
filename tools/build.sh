#!/usr/bin/env bash
# Rebuild every generated page.
#
#   bash tools/build.sh          # rebuild from committed derived data
#   bash tools/build.sh --all    # also recompute from raw material in ../source/
#
# Pages in public/ are GENERATED. Editing them by hand loses the change on the next
# build; edit the builder in tools/ instead.
#
# Stages marked [raw] need uncommitted source material. They write AGGREGATES into
# tools/derived/, which is committed, so every page rebuilds on a fresh checkout
# without the raw material ever being present.
#
# TWO PASSES, deliberately. Pages link to each other only once the target file
# exists, so a link is never offered as a 404. Those references can be circular,
# which no single ordering satisfies on a clean tree: the first pass creates the
# files, the second resolves the links.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
ALL=${1:-}

run () { echo; echo "==> $1"; shift; "$@"; }

pages () {
  $PY tools/build_guide.py
  $PY tools/build_index.py    # last: it links to every guide page that now exists
}

echo; echo "==> pages, pass 1 of 2"; pages
echo; echo "==> pages, pass 2 of 2 (resolves cross-links)"; pages
run "notebook navigation"        $PY tools/inject_nav.py
run "validate the manifest"      $PY tools/manifest.py
run "check every link resolves"  $PY tools/check_links.py
run "check the house rules"      $PY tools/check_content.py
run "check the notebook shape"   $PY tools/check_notebooks.py

echo
echo "==> done."
