#!/usr/bin/env bash
# Regenerate the two social cards from their HTML sources.
#
#   bash assets/social/render.sh
#
# linkedin-card.png  1200x627 (1.91:1)  -> Open Graph / LinkedIn / Twitter.
#                                          Copied into public/assets/img/social-card.png,
#                                          which is the file the live pages reference.
# github-card.png    1280x640 (2:1)     -> repo Settings > Social preview (manual upload;
#                                          GitHub has no API for it).
#
# Uses $CHROME if set, then Google Chrome on a Mac, then the Chromium a Claude Code cloud
# session has preinstalled, then chromium or google-chrome on the PATH.
set -euo pipefail
cd "$(dirname "$0")"
for candidate in "${CHROME:-}" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
                 /opt/pw-browsers/chromium "$(command -v chromium || true)" \
                 "$(command -v google-chrome || true)"; do
  [ -n "$candidate" ] && [ -x "$candidate" ] && { CHROME="$candidate"; break; }
done
[ -x "${CHROME:-}" ] || { echo "No Chrome or Chromium found. Set CHROME to its path." >&2; exit 1; }
# Linux runs a session as root, and Chromium refuses to start as root inside its sandbox
SANDBOX=""
[ "$(uname)" = Linux ] && SANDBOX="--no-sandbox"

shot () {  # shot <html> <out> <w> <h>
  "$CHROME" --headless $SANDBOX --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --screenshot="$PWD/$2" --window-size="$3,$4" "file://$PWD/$1" >/dev/null 2>&1
  echo "  $2  ${3}x${4}"
}
shot card-linkedin.html linkedin-card.png 1200 627
shot card-github.html   github-card.png   1280 640

mkdir -p ../../public/assets/img
cp linkedin-card.png ../../public/assets/img/social-card.png
echo "  copied linkedin-card.png -> public/assets/img/social-card.png"
