#!/usr/bin/env python3
import csv, re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent
ODS_CSV = Path('/tmp/opencode/import/ListaInvFisic.csv')
PRODUCTO_CSV = BASE / 'Producto.csv'
OUTPUT = BASE / 'Stock_Reconciliation_Import.csv'

# ── 1. Product lookup ──
name_to_code = {}
name_to_rate = {}
with open(PRODUCTO_CSV, newline='', encoding='utf-8-sig') as f:
    next(csv.reader(f))
    for row in csv.reader(f):
        if len(row) < 4: continue
        code = row[0].strip()
        name = row[3].strip()
        rate = row[8].strip() if len(row) > 8 else ''
        if name and code:
            name_to_code[name] = code
            if rate: name_to_rate[name] = rate

# ── 2. Parse inventory ──
WH_MAP = {
    'CASA MATRIZ': 'CASA MATRIZ - Imgraf', 'COJUTEPEQUE': 'COJUTEPEQUE - Imgraf',
    'ESPAÑA': 'ESPAÑA - Imgraf', 'SAN MIGUEL': 'SAN MIGUEL - Imgraf',
    'SANTA ANA': 'SANTA ANA - Imgraf', 'SONSONATE': 'SONSONATE - Imgraf',
}
agg = defaultdict(lambda: {'qty': 0, 'rate': ''})
cur_wh = None

with open(ODS_CSV, newline='', encoding='utf-8-sig') as f:
    for cols in csv.reader(f):
        if not cols or not cols[0].strip(): continue
        c0 = cols[0].strip()
        m = re.match(r'^Almacen:\s*(.+)$', c0)
        if m:
            wh = m.group(1).strip()
            cur_wh = WH_MAP.get(wh)
            continue
        if cur_wh is None or len(cols) < 5: continue
        name = cols[0].strip()
        tipo = cols[1].strip() if len(cols) > 1 else ''
        if not name or tipo.lower() == 'servicio': continue
        try:
            q = float(cols[4].strip().replace(',', ''))
        except:
            q = 0
        if q <= 0: continue
        code = name_to_code.get(name)
        if not code:
            for n, c in name_to_code.items():
                if n.lower() == name.lower(): code = c; break
        if not code: continue
        key = (code, cur_wh)
        agg[key]['qty'] += int(q)
        if not agg[key]['rate']:
            agg[key]['rate'] = name_to_rate.get(name, '')

# ── 3. Item info lookup ──
code_to_name, code_to_group = {}, {}
with open(PRODUCTO_CSV, newline='', encoding='utf-8-sig') as f:
    next(csv.reader(f))
    for row in csv.reader(f):
        if len(row) < 4: continue
        code = row[0].strip()
        if code:
            code_to_name[code] = row[3].strip()
            code_to_group[code] = row[1].strip() if len(row) > 1 else ''

# ── 4. Write template format (Items(2).csv style) ──
HEADER = [
    ['Editar en masa Items'],
    ['Barcode','Has Item Scanned','Item Code','Item Name','Item Group','Warehouse','Quantity','Stock UOM','Valuation Rate','Amount','Allow Zero Valuation Rate','Use Serial No / Batch Fields','Reconcile All Serial Nos / Batches','Serial / Batch Bundle','Current Serial / Batch Bundle','Serial No','Batch No','Current Qty','Current Amount','Current Valuation Rate','Current Serial No','Quantity Difference','Amount Difference'],
    ['barcode','has_item_scanned','item_code','item_name','item_group','warehouse','qty','stock_uom','valuation_rate','amount','allow_zero_valuation_rate','use_serial_batch_fields','reconcile_all_serial_batch','serial_and_batch_bundle','current_serial_and_batch_bundle','serial_no','batch_no','current_qty','current_amount','current_valuation_rate','current_serial_no','quantity_difference','amount_difference'],
]

with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    for h in HEADER:
        w.writerow(h)
    for (code, wh), v in sorted(agg.items()):
        row = [''] * 23
        row[2] = code  # item_code
        row[3] = code_to_name.get(code, '')  # item_name
        row[4] = code_to_group.get(code, '')  # item_group
        row[5] = wh  # warehouse
        row[6] = str(v['qty'])  # qty
        row[7] = 'Nos'  # stock_uom
        row[8] = v['rate']  # valuation_rate
        row[10] = '1'  # allow_zero_valuation_rate
        w.writerow(row)

print(f"Done: {OUTPUT} — {len(agg)} entries, {sum(v['qty'] for v in agg.values())} total qty")
