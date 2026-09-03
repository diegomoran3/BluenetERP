import frappe, csv, os
SRC = "/tmp/import_data"
csvpath = os.path.join(SRC, "Tipo_Grupos.csv")
if os.path.exists(csvpath):
    count = 0
    with open(csvpath, newline="", encoding="utf-8") as f:
        next(f)
        for row in csv.reader(f):
            name = row[1].strip() if len(row) > 1 else ""
            if not name or frappe.db.exists("Item Group", name):
                continue
            frappe.get_doc({"doctype": "Item Group", "item_group_name": name, "parent_item_group": "All Item Groups"}).insert()
            count += 1
    print(f"Item Groups: {count} created")
else:
    print("SKIP Tipo_Grupos.csv - not found")
csvpath = os.path.join(SRC, "Almacenes.csv")
if os.path.exists(csvpath):
    count = 0
    with open(csvpath, newline="", encoding="utf-8") as f:
        next(f)
        for row in csv.reader(f):
            name = row[1].strip() if len(row) > 1 else ""
            if not name or frappe.db.exists("Warehouse", name):
                continue
            frappe.get_doc({"doctype": "Warehouse", "warehouse_name": name, "parent_warehouse": "All Warehouses"}).insert()
            count += 1
    print(f"Warehouses: {count} created")
else:
    print("SKIP Almacenes.csv - not found")
frappe.db.commit()
print("Done.")