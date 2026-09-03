import frappe, os, csv

SRC = "/tmp/import_images"
CSV = "/tmp/import_data/Articulo.csv"

# item_code -> filename mapping
if os.path.exists(CSV):
    with open(CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["codigo"].strip()
            img = row["rutafoto"].strip()
            if not img or not frappe.db.exists("Item", code):
                continue
            path = os.path.join(SRC, img)
            if not os.path.exists(path):
                continue
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": img,
                "is_private": 0,
                "attached_to_doctype": "Item",
                "attached_to_name": code,
                "content": open(path, "rb").read(),
            })
            file_doc.save(ignore_permissions=True)
            frappe.db.set_value("Item", code, "image", file_doc.file_url)
    frappe.db.commit()
