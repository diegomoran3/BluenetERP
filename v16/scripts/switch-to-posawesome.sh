#!/bin/bash
# Switch site to POS-Awesome
set -e
SITE="${1:-localhost}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== Switching to POS-Awesome ==="

# Uninstall KLiK if installed
echo "Uninstalling klik_pos..."
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" uninstall-app klik_pos --yes 2>/dev/null || echo "(not installed)"

# Install POS-Awesome if not already
echo "Installing posawesome..."
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" install-app posawesome 2>/dev/null || echo "(already installed)"

# Run migrate to sync fixtures
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" migrate 2>/dev/null

echo ""
echo "=== POS-Awesome ready ==="
echo "Access via workspace 'POS Awesome' in the sidebar"
