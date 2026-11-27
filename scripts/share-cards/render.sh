#!/bin/sh
# Render the 1200x630 OpenGraph share cards into static/assets/.
# Usage: scripts/share-cards/render.sh  (needs Google Chrome; then run collectstatic)
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
for card in turnpiece temphist; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --allow-file-access-from-files --window-size=1200,630 \
    --screenshot="../../static/assets/og-$card.png" "file://$PWD/$card.html" 2>/dev/null
done
