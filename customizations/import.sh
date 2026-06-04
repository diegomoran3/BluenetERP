#!/bin/bash
# Imports customizations (Custom Fields, Client Scripts) from JSON files.
# Usage: ./import.sh [site=localhost]
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-localhost}"
CONTAINER="bluenet-backend-1"

echo "=== Importing customizations to site: $SITE ==="

docker cp "$DIR/data" "$CONTAINER:/tmp/custom_data"
docker cp "$DIR/import.py" "$CONTAINER:/tmp/custom_import.py"
docker exec "$CONTAINER" bash -c \
  "cd /home/frappe/frappe-bench && cat /tmp/custom_import.py | bench --site $SITE console"

echo "=== Done ==="
echo ""
echo "Post-import setup:"
echo "  1. bench --site $SITE set-config server_script_enabled 1"
echo "     (enables server scripts — required for auto-naming)"
echo "  2. Set Stock Settings → Item Naming By → 'Naming Series' in the UI"
echo "  3. Edit each Item Group → set its naming series pattern"
