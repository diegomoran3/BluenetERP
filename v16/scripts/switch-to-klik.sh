#!/bin/bash
# Switch site to KLiK PoS
set -e
SITE="${1:-localhost}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== Switching to KLiK PoS ==="

# Uninstall POS-Awesome if installed
echo "Uninstalling posawesome..."
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" uninstall-app posawesome --yes 2>/dev/null || echo "(not installed)"

# Install KLiK if not already
echo "Installing klik_pos..."
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" install-app klik_pos 2>/dev/null || echo "(already installed)"

# Run migrate to sync fixtures
docker compose -p bluenet -f compose.yaml exec backend \
  bench --site "$SITE" migrate 2>/dev/null

# Add all leaf item groups to POS Profile
echo "Configuring POS Profile..."
docker compose -p bluenet -f compose.yaml exec backend \
  bash -c "cd /home/frappe/frappe-bench && echo '
import frappe
pos_name = frappe.get_list(\"POS Profile\", pluck=\"name\", limit=1)
if pos_name:
    pos = frappe.get_doc(\"POS Profile\", pos_name[0])
    pos.item_groups = []
    for g in frappe.get_list(\"Item Group\", filters={\"is_group\": 0}, pluck=\"name\"):
        pos.append(\"item_groups\", {\"item_group\": g})
    pos.save(ignore_permissions=True)
    frappe.db.commit()
    print(f\"Item groups added to {pos_name[0]}\")
else:
    print(\"No POS Profile found\")
' | bench --site '$SITE' console"

echo ""
echo "=== KLiK PoS ready ==="
echo "Access at http://erpnext.site.com/klik_pos"
