import frappe

WH = "CASA MATRIZ - Imgraf"
COMPANY = "Importadora Grafica"
POS_NAME = "CASA MATRIZ"

if not frappe.db.exists("POS Profile", POS_NAME):
    doc = frappe.get_doc({
        "doctype": "POS Profile",
        "name": POS_NAME,
        "company": COMPANY,
        "warehouse": WH,
        "country": "El Salvador",
        "currency": "USD",
        "write_off_account": "Stock Adjustment - Imgraf",
        "write_off_cost_center": "Main - Imgraf",
        "income_account": "Sales - Imgraf",
        "expense_account": "Cost of Goods Sold - Imgraf",
        "cost_center": "Main - Imgraf",
        "selling_price_list": "Standard Selling",
        "applicable_for_users": [{"user": "Administrador", "default": 1}],
    })
    doc.insert()
    print(f"POS Profile '{POS_NAME}' created")
else:
    profile = frappe.get_doc("POS Profile", POS_NAME)
    exists = [u.user for u in profile.applicable_for_users]
    if "Administrador" not in exists:
        profile.append("applicable_for_users", {"user": "Administrador", "default": 1})
        profile.save()
        print(f"Added Administrador to '{POS_NAME}'")
    else:
        print(f"POS Profile '{POS_NAME}' already has Administrador")

frappe.db.commit()
print("Done.")
