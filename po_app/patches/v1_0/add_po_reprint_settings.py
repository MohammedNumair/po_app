import frappe

def execute():
    """
    Patch to add:
    1. Child DocType 'PO Reprint User'
    2. Table field on Buying Settings: po_reprint_users
    3. Hidden Int field on Purchase Order: print_count
    """

    # 1) Create child DocType "PO Reprint User" (table)
    if not frappe.db.exists("DocType", "PO Reprint User"):
        dt = frappe.new_doc("DocType")
        dt.name = "PO Reprint User"
        dt.module = "Buying"       # keep it under Buying module
        # dt.custom = 1              # mark as custom
        dt.istable = 1             # marks this as child table

        # add child field properly
        dt.append("fields", {
            "fieldname": "user",
            "label": "User",
            "fieldtype": "Link",
            "options": "User",
            "reqd": 1,
            "in_list_view": 1
        })

        dt.append("permissions", {
            "role": "Administrator",
            "read": 1,
            "write": 1
        })

        dt.insert(ignore_if_duplicate=True)
        frappe.db.commit()

    # 2) Add Table field on Buying Settings
    if not frappe.db.exists("Custom Field", {"dt": "Buying Settings", "fieldname": "po_reprint_users"}):
        cf = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Buying Settings",
            "fieldname": "po_reprint_users",
            "label": "PO Reprint Authorized Users",
            "fieldtype": "Table",
            "options": "PO Reprint User",
            "insert_after": "default_print_format"  # adjust if needed
        })
        cf.insert()
        frappe.db.commit()

    # 3) Add Int field on Purchase Order
    if not frappe.db.exists("Custom Field", {"dt": "Purchase Order", "fieldname": "print_count"}):
        cf2 = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Purchase Order",
            "fieldname": "print_count",
            "label": "Print Count",
            "fieldtype": "Int",
            "default": "0",
            "hidden": 1,
            "insert_after": "status"
        })
        cf2.insert()
        frappe.db.commit()
