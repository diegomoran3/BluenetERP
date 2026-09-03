import csv, xlrd, re

# ── Group lookup ────────────────────────────────────────────
wb = xlrd.open_workbook("import/Tipo_Grupos.xls")
ws = wb.sheet_by_index(0)
group_map = {}
for r in range(1, ws.nrows):
    code = str(int(ws.cell_value(r, 0)))
    name = str(ws.cell_value(r, 1)).strip()
    group_map[code] = name

# ── UOM ─────────────────────────────────────────────────────
def guess_uom(name):
    return "Yard" if re.search(r"\byard[as]?\b|\byards\b", name.lower()) else "Unit"

# ── Read items ──────────────────────────────────────────────
wb = xlrd.open_workbook("import/Articulo.xls")
ws = wb.sheet_by_index(0)

headers = [
    "Código del Producto", "Grupo de Productos",
    "Unidad de Medida (UdM) predeterminada", "Nombre del Producto",
    "Deshabilitado", "Mantener Stock", "Permitir Ventas", "Permitir Compra",
    "Precio de venta estándar", "Imagen",
    "Unidad de Medida (UdM)",
    "Unidad de Medida de Compra Predeterminada",
    "Unidad de Medida de Ventas Predeterminada",
    "Almacén por defecto (Valores por Defecto del Artículo)",
    "Compañía (Valores por Defecto del Artículo)",
]

with open("import/Producto.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(headers)
    for r in range(1, ws.nrows):
        vals = [str(ws.cell_value(r, c)) for c in range(ws.ncols)]
        code, name, grupo_cod = vals[0], vals[1], vals[2]
        usaexist, tipo_item = vals[4], vals[5]
        imagen = vals[6]
        precio_1 = float(vals[8]) if vals[8] else 0
        grupo_nom = group_map.get(grupo_cod, "All Item Groups")
        uom = guess_uom(name)

        w.writerow([
            code, grupo_nom, uom, name, "0",
            "1" if usaexist == "1" else "0",
            "1" if tipo_item == "1" else "0",
            "1" if tipo_item == "1" else "0",
            f"{precio_1:.2f}" if precio_1 > 0 else "",
            f"image/{imagen}" if imagen else "",
            uom, uom, uom,
            "CASA MATRIZ - Imgraf",
            "Importadora Grafica",
        ])

with_img = sum(1 for r in range(1, ws.nrows)
               if str(ws.cell_value(r, 6)).strip())
print(f"Producto.csv — {ws.nrows - 1} items ({with_img} with images)")
