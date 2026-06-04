import frappe, json, os

SRC = "/tmp/custom_data"

def load_and_insert(filename, doctype):
    path = os.path.join(SRC, filename)
    if not os.path.exists(path):
        print(f"Skipping {filename} — not found")
        return
    with open(path) as f:
        records = json.load(f)
    for record in records:
        name = record.get("name")
        if name and frappe.db.exists(doctype, name):
            doc = frappe.get_doc(doctype, name)
            doc.update(record)
            doc.save()
            print(f"Updated {doctype}: {name}")
        else:
            try:
                doc = frappe.get_doc(doctype, record)
                doc.insert()
                print(f"Created {doctype}: {doc.name}")
            except frappe.DuplicateEntryError:
                print(f"Skipped {doctype}: {record.get('name')} — already exists")

load_and_insert("custom_field_item_group.json", "Custom Field")
load_and_insert("client_script_item.json", "Client Script")
load_and_insert("server_script_item.json", "Server Script")

frappe.db.commit()
print("Import complete.")
