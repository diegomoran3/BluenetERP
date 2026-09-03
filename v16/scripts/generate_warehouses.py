import csv, xlrd

wb = xlrd.open_workbook("import/Almacenes.xls")
ws = wb.sheet_by_index(0)

headers = ["ID", "Nombre del Almacén", "Compañía", "Deshabilitado",
           "Es Almacén de Grupo", "Almacén Padre"]

with open("import/Almacenes_import.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(headers)
    for r in range(1, ws.nrows):
        name = str(ws.cell_value(r, 1)).strip()
        if name:
            w.writerow([f"Imgraf - {name}", name, "Importadora Grafica", 0, 0, ""])

print(f"Almacenes_import.csv — {ws.nrows - 1} warehouses")
