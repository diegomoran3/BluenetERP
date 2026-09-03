#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-localhost}"
CONTAINER="bluenet-backend-1"
TMPDIR="/tmp/import_csv_$$"
mkdir -p "$TMPDIR"

echo "=== Step 1: Convert XLS to CSV ==="
libreoffice --headless --convert-to csv --outdir "$TMPDIR" "$DIR/Tipo_Grupos.xls" 2>/dev/null
libreoffice --headless --convert-to csv --outdir "$TMPDIR" "$DIR/Almacenes.xls" 2>/dev/null

echo "=== Step 2: Copy CSV files to container ==="
docker exec "$CONTAINER" bash -c "mkdir -p /tmp/import_data"
docker cp "$TMPDIR/Tipo_Grupos.csv" "$CONTAINER:/tmp/import_data/Tipo_Grupos.csv"
docker cp "$TMPDIR/Almacenes.csv" "$CONTAINER:/tmp/import_data/Almacenes.csv"
docker cp "$DIR/import_item_groups_warehouses.py" "$CONTAINER:/tmp/import_item_groups_warehouses.py"

echo "=== Step 3: Import into ERPNext ==="
docker exec "$CONTAINER" bash -c \
  "cd /home/frappe/frappe-bench && bench --site $SITE console < /tmp/import_item_groups_warehouses.py"

rm -rf "$TMPDIR"
echo "=== Done ==="
