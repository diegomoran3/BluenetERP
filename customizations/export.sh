#!/bin/bash
# Exports customizations (Custom Fields, Client Scripts) to JSON files.
# Usage: ./export.sh [site=localhost]
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-localhost}"
CONTAINER="bluenet-backend-1"

echo "=== Exporting customizations from site: $SITE ==="

docker cp "$DIR/export.py" "$CONTAINER:/tmp/custom_export.py"
docker exec "$CONTAINER" bash -c \
  "cd /home/frappe/frappe-bench && cat /tmp/custom_export.py | bench --site $SITE console"

rm -rf "$DIR/data"
docker cp "$CONTAINER:/tmp/custom_data" "$DIR/data" 2>/dev/null

echo "=== Done — data in $DIR/data/ ==="
