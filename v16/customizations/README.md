# Customizations

Portable, git-tracked Frappe customizations for BluenetERP.

Changes made in the UI (custom fields, client scripts, server scripts) are
exported as JSON so they can be version-controlled and deployed to any machine.

## Contents

| File | Description |
|------|-------------|
| `export.sh` | Export customizations from running site to JSON |
| `import.sh` | Import customizations from JSON into running site |
| `export.py` | Python logic for export |
| `import.py` | Python logic for import |
| `data/` | JSON exports (tracked in git) |

### Data files

| File | Content |
|------|---------|
| `custom_field_item_group.json` | Custom field `Naming Series` on Item Group |
| `client_script_item.json` | Client Script — auto-fills naming series on Item form |
| `server_script_item.json` | Server Script — generates item code on save (Before Save hook) |

## Current customizations

1. **Naming Series field on Item Group** — Set a naming pattern per group
   (e.g. `ELEC-.#####` for Electronics, `FURN-.#####` for Furniture)

2. **Auto-fill naming series on Item (Client Script)** — When creating a new
   Item and selecting an Item Group, the naming series is auto-filled from
   the group's pattern for visual feedback.

3. **Auto-generate item code (Server Script)** — On Before Save, generates
   the item code from the group's pattern. Works for UI, API, and bulk imports.

Example: Item Group "Consumable" with pattern `CONS-.#####` creates
`CONS-00001`, `CONS-00002`, etc.

## Workflow

### Export (after making UI changes)

```bash
./customizations/export.sh [site]
git add customizations/
git commit -m "update customizations"
```

### Import (on new deployment)

```bash
./customizations/import.sh [site]
```

Then:

1. `bench --site [site] set-config server_script_enabled 1`
2. Go to **Stock Settings** > set **Item Naming By** > **"Naming Series"**
3. Edit each **Item Group** > set its **Naming Series** pattern
