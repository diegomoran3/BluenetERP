#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-localhost}"
CONTAINER="bluenet-backend-1"

echo "=== Copy images to container ==="
docker cp "$DIR/images" "$CONTAINER:/tmp/import_images"
docker cp "$DIR/attach_images.py" "$CONTAINER:/tmp/attach_images.py"

echo "=== Attaching images to items ==="
docker exec "$CONTAINER" bash -c \
  "cd /home/frappe/frappe-bench && cat /tmp/attach_images.py | bench --site $SITE console"

echo "=== Done ==="
