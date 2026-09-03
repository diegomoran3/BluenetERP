#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent / 'import'
ODS_CSV = Path('/tmp/opencode/import/ListaInvFisic.csv')
PRODUCTO_CSV = BASE / 'Producto.csv'
OUTPUT = BASE / 'Stock_Reconciliation_Import.csv'

# ── 1. Build name→code and name→rate mappings from Producto.csv ──
name_to_code = {}
name_to_rate = {}
with open(PRODUCTO_CSV, newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if not row or len(row) < 4:
            continue
        code = row[0].strip()
        name = row[3].strip()
        rate = row[8].strip() if len(row) > 8 else ''
        if name and code:
            name_to_code[name] = code
            if rate:
                name_to_rate[name] = rate

print(f"Producto.csv: {len(name_to_code)} products loaded")

# ── 2. Parse ListaInvFisic.csv ──
# ERPNext warehouse names (from Almacenes_import.csv ID column)
WAREHOUSE_MAP = {
    'CASA MATRIZ': 'CASA MATRIZ - Imgraf',
    'COJUTEPEQUE': 'COJUTEPEQUE - Imgraf',
    'ESPAÑA': 'ESPAÑA - Imgraf',
    'SAN MIGUEL': 'SAN MIGUEL - Imgraf',
    'SANTA ANA': 'SANTA ANA - Imgraf',
    'SONSONATE': 'SONSONATE - Imgraf',
}

agg = defaultdict(lambda: {'qty': 0, 'rate': ''})
current_warehouse = None
unmatched_names = []

with open(ODS_CSV, newline='', encoding='utf-8-sig') as f:
    lines = list(csv.reader(f))

for cols in lines:
    if not cols or not cols[0].strip():
        continue
    cell0 = cols[0].strip()

    m = re.match(r'^Almacen:\s*(.+)$', cell0)
    if m:
        wh = m.group(1).strip()
        current_warehouse = WAREHOUSE_MAP.get(wh)
        continue

    if current_warehouse is None:
        continue
    if len(cols) < 5:
        continue

    name = cols[0].strip()
    tipo = cols[1].strip() if len(cols) > 1 else ''
    cantidad_str = cols[4].strip() if len(cols) > 4 else '0'

    if not name or tipo.lower() == 'servicio':
        continue

    try:
        cantidad = float(cantidad_str.replace(',', ''))
    except ValueError:
        cantidad = 0

    if cantidad <= 0:
        continue

    item_code = name_to_code.get(name)
    if not item_code:
        for n, c in name_to_code.items():
            if n.lower() == name.lower():
                item_code = c
                break
    if not item_code:
        unmatched_names.append(name)
        continue

    key = (item_code, current_warehouse)
    agg[key]['qty'] += int(cantidad)
    if not agg[key]['rate']:
        agg[key]['rate'] = name_to_rate.get(name, '')

if unmatched_names:
    print(f"\nWARNING: {len(unmatched_names)} products had no match in Producto.csv:")
    for n in sorted(set(unmatched_names)):
        print(f"  - {n}")

# ── 3. Template header (ERPNext Stock Reconciliation Items format) ──
TEMPLATE_HEADER = [
    ['Editar en masa Items'],
    ['Barcode','Has Item Scanned','Item Code','Item Name','Item Group','Warehouse','Quantity','Stock UOM','Valuation Rate','Amount','Allow Zero Valuation Rate','Use Serial No / Batch Fields','Reconcile All Serial Nos / Batches','Serial / Batch Bundle','Current Serial / Batch Bundle','Serial No','Batch No','Current Qty','Current Amount','Current Valuation Rate','Current Serial No','Quantity Difference','Amount Difference'],
    ['barcode','has_item_scanned','item_code','item_name','item_group','warehouse','qty','stock_uom','valuation_rate','amount','allow_zero_valuation_rate','use_serial_batch_fields','reconcile_all_serial_batch','serial_and_batch_bundle','current_serial_and_batch_bundle','serial_no','batch_no','current_qty','current_amount','current_valuation_rate','current_serial_no','quantity_difference','amount_difference'],
    [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
    ['El formato CSV es sensible a mayúsculas y minúsculas'],
    ['No edite los encabezados que están preestablecidos en la plantilla'],
    ['------'],
    ['','','','','','','','Nos','','','',1,'','','','','','','','','','',''],
]

# Column indexes in the template (0-based)
IDX_ITEM_CODE = 2
IDX_ITEM_NAME = 3
IDX_ITEM_GROUP = 4
IDX_WAREHOUSE = 5
IDX_QTY = 6
IDX_STOCK_UOM = 7
IDX_VAL_RATE = 8
IDX_ALLOW_ZERO_VAL = 10

# Build lookup: item_code → name, group from Producto.csv
code_to_name = {}
code_to_group = {}
with open(PRODUCTO_CSV, newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if not row or len(row) < 4:
            continue
        code = row[0].strip()
        name = row[3].strip()
        group = row[1].strip() if len(row) > 1 else ''
        if code:
            code_to_name[code] = name
            code_to_group[code] = group

# ── 4. Write final CSV ──
with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    for h_row in TEMPLATE_HEADER:
        w.writerow(h_row)
    for (code, wh), v in sorted(agg.items()):
        row = [''] * 23
        row[IDX_ITEM_CODE] = code
        row[IDX_ITEM_NAME] = code_to_name.get(code, '')
        row[IDX_ITEM_GROUP] = code_to_group.get(code, '')
        row[IDX_WAREHOUSE] = wh
        row[IDX_QTY] = str(v['qty'])
        row[IDX_STOCK_UOM] = 'Nos'
        row[IDX_VAL_RATE] = v['rate']
        row[IDX_ALLOW_ZERO_VAL] = '1'
        w.writerow(row)

print(f"\nStock Reconciliation CSV: {OUTPUT}")
print(f"Total entries: {len(agg)}")
warehouses = set(k[1] for k in agg)
print(f"Warehouses: {', '.join(sorted(warehouses))}")
total_qty = sum(v['qty'] for v in agg.values())
print(f"Total quantity: {total_qty}")
