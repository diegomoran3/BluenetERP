# Data Import Guide

## Source Files

| File | Doctype | Records | Notes |
|------|---------|---------|-------|
| `Tipo_Grupos.xls` | Item Group | 14 | codigo → group name mapping |
| `Almacenes.xls` | Warehouse | 7 | 6 sucursales, DOCTOR PRINT removed |
| `Tipo_Precios.xls` | Price List | 6 | PRECIO #1 – PRECIO #6 |
| `Articulo.xls` | Item | 513 | Simplified, 39 cols |
| `Clientes.xls` | Customer | ~566 | Pending import |

## Known Mappings

### Item (Articulo.xls) → Producto.csv

| Articulo field | CSV column | Notes |
|---|---|---|
| `codigo` | Código del Producto | Direct |
| `nombre` | Nombre del Producto | Direct |
| `codigo_grupo` | Grupo de Productos | Mapped via Tipo_Grupos lookup (numeric → name) |
| `usaexist` | Mantener Stock | 1 = track stock, 0 = don't (only 3 services have 0) |
| `tipo_item` | Permitir Ventas / Compra | 0 = service, 1 = product |
| `precio_1` | Precio de venta estándar | Only one price fits in Item; precio_2..6 need separate Item Price import |
| `rutafoto` | Imagen | Path: `image/filename` — put CSV + `images/` folder together when uploading |
| `impuesto_venta_1` | — | NOT imported yet. Values: 20, 55, C3. Needs Item Tax Template setup first |

### UOM Logic

Rule applied in final version:
- **Yard** if name contains `yarda`, `yards`, `yard` (8 items)
- **Unit** for everything else (505 items)

Previous attempts tried keyword-based classifiers for vinyl/banner/rollo/vinil — too many false positives. Simple rule was preferred.

### Warehouse

- ID format: `{warehouse_name} - Imgraf` (e.g., `CASA MATRIZ - Imgraf`)
- Parent structure: `Todos los almacenes - Imgraf` → `Sucursales - Imgraf` → each sucursal
- Company: `Importadora Grafica` (abbr: `Imgraf`)

### Company

- **Name**: Importadora Grafica
- **Abbreviation**: Imgraf (used in warehouse naming as `- Imgraf` suffix)

### Price Lists (pending)

`precio_1` through `precio_6` map to the 6 price lists from `Tipo_Precios.xls`:
- PRECIO #1 → `precio_1` (already in Item as standard rate)
- PRECIO #2–#6 → need separate Item Price import

### Images

- Source: `import/images/` (121 files, ~25MB)
- CSV path: `image/filename` (relative path)
- Upload method: ZIP the CSV + `images/` folder together in Data Import
- Items with images: 288 out of 513

### Taxes (pending)

`impuesto_venta_1` values:
- `20` — likely 20% VAT
- `55` — unknown rate
- `C3` — custom code

Only one Item Tax Template exists: `El Salvador Tax - Imgraf`. Either map all to that or create separate templates first.

## Stock Reconciliation (Initial Inventory)

Source: `ListaInvFisic.ods` — physical inventory count per warehouse.

Products are matched by name against `Producto.csv` (no codes in the ODS). The script:
1. Parses `ListaInvFisic.ods` (converted to CSV), reads each warehouse section
2. Looks up each product name in `Producto.csv` to get `item_code` and `valuation_rate`
3. Aggregates qty by `(item_code, warehouse)` (some products appear multiple times per warehouse)
4. Writes output matching the `Items(2).csv` template format

**Excluded**: DOCTOR PRINT warehouse, service-type products (tipo=Servicio), "TODOS" summary section, zero-qty items.

### Usage
```bash
python3 scripts/generate_stock_reconciliation.py
```

Output: `import/Stock_Reconciliation_Import.csv`

### Template
`import/Items(2).csv` — downloaded from ERPNext (Conciliación de Stock > Items child table).

Warehouse names in ERPNext follow the pattern `{NAME} - Imgraf` (e.g. `CASA MATRIZ - Imgraf`).

### Stats (June 2026)
| Metric | Value |
|---|---|
| Products matched | 500/500 |
| Stock entries | 1,387 |
| Total quantity | 130,412 |
| Warehouses | 6 (all except DOCTOR PRINT) |

## Import Order (Recommended)

1. ✅ Item Group (Tipo_Grupos.xls)
2. ✅ Warehouse (Almacenes.xls)
3. ✅ Item (Producto.csv)
4. ✅ Stock Reconciliation (ListaInvFisic.ods → Stock_Reconciliation_Import.csv)
5. Price List (Tipo_Precios.xls)
6. Customer (Clientes.xls)
7. Item Price (precio_2..6)
8. Taxes (after templates are set up)

## Technical Notes

- ERPNext v16.19.1, Frappe bench inside Docker
- Container: `bluenet-backend-1`, site: `localhost`
- Data Import via UI: open doctype list → 🗂 Menu → Import
- Image paths in CSV are relative — place CSV at root level with `images/` subfolder
- Warehouse rename is NOT allowed (must delete and re-create)
- All CSVs are UTF-8 BOM encoded (standard for ERPNext)
