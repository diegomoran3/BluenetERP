#!/usr/bin/env python3
"""POS Switcher for Bluenet ERPNext — switch between KLiK PoS and POS-Awesome."""

import subprocess, sys, os

SITE = "localhost"
PROJECT = "/home/diego/sources/BluenetERP"
BACKEND = "bluenet-backend-1"

def run(cmd, check=True, silent=False):
    prefix = ["docker", "compose", "-p", "bluenet", "-f", f"{PROJECT}/compose.yaml", "exec", BACKEND]
    full = prefix + ["bench", "--site", SITE] + cmd.split()
    r = subprocess.run(full, capture_output=True, text=True)
    if r.returncode and check:
        if not silent or "not installed" not in r.stderr:
            print(f"  ERROR: {r.stderr[:200]}")
            return False
    if not silent:
        for line in r.stdout.splitlines():
            print(f"  {line}")
    return True

def run_stdin(code):
    prefix = ["docker", "compose", "-p", "bluenet", "-f", f"{PROJECT}/compose.yaml", "exec", "-T", BACKEND]
    full = prefix + ["bash", "-c", f"cd /home/frappe/frappe-bench && echo {shquote(code)} | bench --site {SITE} console"]
    r = subprocess.run(full, capture_output=True, text=True, timeout=60)
    if r.returncode:
        print(f"  ERROR: {r.stderr[:200]}")
        return False
    for line in r.stdout.splitlines():
        if line.strip() and not line.startswith("In [") and not line.startswith("Apps in"):
            print(f"  {line}")
    return True

def shquote(s):
    import shlex
    return shlex.quote(s)

def get_installed():
    r = subprocess.run(
        ["docker", "compose", "-p", "bluenet", "-f", f"{PROJECT}/compose.yaml", "exec", BACKEND,
         "bench", "--site", SITE, "list-apps"],
        capture_output=True, text=True, timeout=15
    )
    return r.stdout

def switch_to_klik():
    print("\n=== Switching to KLiK PoS ===")
    run("uninstall-app posawesome --yes", check=False, silent=True)
    run("install-app klik_pos", check=False, silent=True)
    run("migrate", silent=True)

    print("\nConfiguring POS Profile...")
    code = """
import frappe
pos_name = frappe.get_list("POS Profile", pluck="name", limit=1)
if pos_name:
    pos = frappe.get_doc("POS Profile", pos_name[0])
    pos.item_groups = []
    for g in frappe.get_list("Item Group", filters={"is_group": 0}, pluck="name"):
        pos.append("item_groups", {"item_group": g})
    pos.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"Added all item groups to {pos_name[0]}")
else:
    print("No POS Profile found")
"""
    prefix = ["docker", "compose", "-p", "bluenet", "-f", f"{PROJECT}/compose.yaml", "exec", "-T", BACKEND]
    full = prefix + ["bash", "-c", f"cd /home/frappe/frappe-bench && echo {shquote(code)} | bench --site {SITE} console"]
    subprocess.run(full, timeout=30)

    print("\n✅ KLiK PoS ready! Access at http://erpnext.site.com/klik_pos")

def switch_to_posawesome():
    print("\n=== Switching to POS-Awesome ===")
    run("uninstall-app klik_pos --yes", check=False, silent=True)
    run("install-app posawesome", check=False, silent=True)
    run("migrate", silent=True)

    print("\n✅ POS-Awesome ready! Access via workspace 'POS Awesome' in the sidebar")

def uninstall_all():
    print("\n=== Uninstalling all POS apps ===")
    run("uninstall-app klik_pos --yes", check=False, silent=True)
    run("uninstall-app posawesome --yes", check=False, silent=True)
    print("\n✅ Both KLiK PoS and POS-Awesome removed")

def main():
    print("=" * 50)
    print("  POS Switcher — Bluenet ERPNext")
    print("=" * 50)

    installed = get_installed()
    has_klik = "klik_pos" in installed
    has_awesome = "posawesome" in installed

    if has_klik:
        print(f"  Currently: KLiK PoS is ACTIVE")
    if has_awesome:
        print(f"  Currently: POS-Awesome is ACTIVE")
    if not has_klik and not has_awesome:
        print("  Currently: No POS app installed")
    print()

    print("  [1] Switch to KLiK PoS")
    print("  [2] Switch to POS-Awesome")
    print("  [3] Uninstall all POS apps")
    print("  [4] Exit")
    print()

    choice = input("  Choose [1-4]: ").strip()

    if choice == "1":
        switch_to_klik()
    elif choice == "2":
        switch_to_posawesome()
    elif choice == "3":
        uninstall_all()
    elif choice == "4":
        print("  Bye!")
        return
    else:
        print("  Invalid choice")
        return

if __name__ == "__main__":
    main()
