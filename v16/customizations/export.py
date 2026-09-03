import frappe, json, os

OUT = "/tmp/custom_data"
os.makedirs(OUT, exist_ok=True)

exports = [
    ("custom_field_item_group.json", "Custom Field", {"dt": "Item Group", "fieldname": "custom_naming_series"}),
    ("client_script_item.json", "Client Script", {"dt": "Item", "name": "Item-Auto-Naming-Series"}),
    ("server_script_item.json", "Server Script", "Item-Auto-Code-from-Group"),
]

for filename, doctype, filters in exports:
    try:
        if isinstance(filters, str):
            doc = frappe.get_doc(doctype, filters)
        else:
            doc = frappe.get_doc(doctype, filters)
        records = [doc.as_dict()]
        path = os.path.join(OUT, filename)
        with open(path, "w") as f:
            json.dump(records, f, indent=2, default=str)
        print(f"Exported {filename}")
    except Exception as e:
        print(f"ERROR exporting {filename}: {e}")
