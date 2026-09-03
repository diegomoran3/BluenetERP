import csv, xlrd

wb = xlrd.open_workbook("import/Tipo_Grupos.xls")
ws = wb.sheet_by_index(0)

with open("import/Item_Groups_import.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["item_group_name", "parent_item_group", "is_group"])
    for r in range(1, ws.nrows):
        name = str(ws.cell_value(r, 1)).strip()
        if name:
            w.writerow([name, "All Item Groups", 0])

print(f"Item_Groups_import.csv — {ws.nrows - 1} groups")
