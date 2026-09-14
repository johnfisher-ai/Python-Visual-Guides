#!/usr/bin/env bash
# Execute notebooks the way CI does: every cell, top to bottom, with no --allow-errors.
#
#   bash tools/run_notebooks.sh notebooks/apis-and-json/03-your-first-request.ipynb [...]
#
# The notebooks workflow runs this, and it is how to check a notebook locally before a push.
# A cell that raises must be tagged raises-exception, or execution stops there. Nothing is
# written back: the executed copies go to $OUT, which is /tmp/out unless set.
#
# RETRIES. A notebook that calls a real service can fail on a shared CI machine for reasons
# that have nothing to do with the notebook. Two pushes failed this way on 14 September 2026,
# both on Open-Meteo, once in the TLS handshake and once waiting for a response, while the same
# requests took under half a second from elsewhere and the same notebooks had passed an hour
# earlier. So a notebook whose failure names a network error runs again after a pause, up to
# three attempts, and a warning records that it needed to. Any other failure fails at once, and
# so does a network failure on the last attempt.
set -uo pipefail
cd "$(dirname "$0")/.."

OUT=${OUT:-/tmp/out}
PAUSE=${RETRY_PAUSE:-60}       # seconds before the second attempt, doubled before the third
ATTEMPTS=3
NETWORK='TimeoutError|ReadTimeout|ConnectTimeout|ConnectionError|URLError|timed out|Temporary failure in name resolution|Connection reset by peer'

if command -v jupyter > /dev/null 2>&1; then
  NBCONVERT=(jupyter nbconvert)
else
  NBCONVERT=(python3 -m nbconvert)
fi

[ $# -gt 0 ] || { echo "usage: bash tools/run_notebooks.sh NOTEBOOK..." >&2; exit 2; }
mkdir -p "$OUT"
fail=0
for nb in "$@"; do
  echo "::group::$nb"
  attempt=1
  while :; do
    if "${NBCONVERT[@]}" --to notebook --execute --ExecutePreprocessor.timeout=600 \
         --output-dir "$OUT" --output "$(basename "$nb")" "$nb" > "$OUT/nbconvert.log" 2>&1; then
      if [ "$attempt" -gt 1 ]; then
        echo "::warning file=$nb::ran on attempt $attempt, after a network failure"
      fi
      echo "ok"
      break
    fi
    cat "$OUT/nbconvert.log"
    if [ "$attempt" -lt "$ATTEMPTS" ] && grep -qE "$NETWORK" "$OUT/nbconvert.log"; then
      wait=$((PAUSE * attempt))
      echo "a request to an outside service failed; running the notebook again in ${wait}s"
      sleep "$wait"
      attempt=$((attempt + 1))
      continue
    fi
    echo "::error file=$nb::this notebook did not run top to bottom"
    fail=1
    break
  done
  echo "::endgroup::"
done
exit $fail
