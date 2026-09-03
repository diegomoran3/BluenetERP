import frappe, random

CUSTOMERS = [
    ("Juan", "Pérez", "San Salvador"),
    ("María", "García", "Santa Tecla"),
    ("Carlos", "López", "Antiguo Cuscatlán"),
    ("Ana", "Martínez", "Soyapango"),
    ("José", "Hernández", "Mejicanos"),
    ("Rosa", "Flores", "San Miguel"),
    ("Pedro", "Ramírez", "Santa Ana"),
    ("Lucía", "Torres", "Apopa"),
    ("Miguel", "Cruz", "Ilopango"),
    ("Sofía", "Reyes", "Zacatecoluca"),
    ("Luis", "Morales", "Usulután"),
    ("Carmen", "Vásquez", "Sonsonate"),
    ("Diego", "Castillo", "Cojutepeque"),
    ("Laura", "Rivera", "La Libertad"),
    ("Daniel", "Rivas", "San Vicente"),
    ("Elena", "Mendoza", "Sensuntepeque"),
    ("Fernando", "Ortiz", "Chalatenango"),
    ("Patricia", "Vega", "Ahuachapán"),
    ("Ricardo", "Castro", "Metapán"),
    ("Mónica", "Guerrero", "Jiquilisco"),
]

count = 0
for first, last, city in CUSTOMERS:
    full_name = f"{first} {last}"
    safe = lambda s: s.lower().translate(str.maketrans("áéíóúñü", "aeiounu"))
    email = f"{safe(first)}.{safe(last)}@example.com"
    if frappe.db.exists("Customer", full_name):
        print(f"Skipping {full_name} (already exists)")
        continue
    mobile = f"7{random.randint(100,999)}-{random.randint(1000,9999)}"
    frappe.get_doc({
        "doctype": "Customer",
        "customer_name": full_name,
        "customer_type": "Individual",
        "customer_group": "Individual",
        "territory": "El Salvador",
        "default_currency": "USD",
        "email_id": email,
        "mobile_no": mobile,
        "city": city,
        "country": "El Salvador",
        "companies": [{"company": "Importadora Grafica"}],
    }).insert(ignore_permissions=True)
    print(f"Created {full_name} ({city})")
    count += 1

frappe.db.commit()
print(f"\nDone! {count} customers created.")
