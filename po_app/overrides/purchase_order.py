import frappe
from frappe import _
from frappe.utils import cint

def validate_po_reprint(doc, print_format=None, style=None, meta=None):
    """
    Restrict Purchase Order reprint to allowed users.
    - Print preview is always allowed
    - First actual print is allowed for any user with print permission
    - Subsequent prints are restricted to allowed reprint users
    """
    is_preview = not frappe.form_dict.get("format")
    
    if is_preview:
        return
    
    user = frappe.session.user

    if user == "Administrator":
        new_count = cint(doc.print_count or 0) + 1
        frappe.db.set_value("Purchase Order", doc.name, "print_count", new_count, update_modified=False)
        return

    current_print_count = cint(frappe.db.get_value("Purchase Order", doc.name, "print_count") or 0)
    
    has_print_permission = frappe.has_permission("Purchase Order", "print", user=user)

    settings = frappe.get_single("Buying Settings")
    allowed_users = [u.user for u in settings.po_reprint_users]

    if current_print_count == 0:
        if has_print_permission:
            frappe.db.set_value("Purchase Order", doc.name, "print_count", 1, update_modified=False)
            return
        else:
            frappe.msgprint(_("You are not authorized to print this Purchase Order."), indicator="red", alert=True)
            raise frappe.PermissionError(_("Printing not allowed"))
    else:
        if user not in allowed_users:
            frappe.msgprint(_("You are not authorized to reprint this Purchase Order."), indicator="red", alert=True)
            raise frappe.PermissionError(_("Reprinting not allowed"))
        else:
            new_count = current_print_count + 1
            frappe.db.set_value("Purchase Order", doc.name, "print_count", new_count, update_modified=False)
            