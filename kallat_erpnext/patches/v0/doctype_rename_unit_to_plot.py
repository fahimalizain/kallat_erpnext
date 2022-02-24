import frappe


def execute():
    if not frappe.db.exists("DocType", "Kallat Unit"):
        return

    frappe.rename_doc("DocType", "Kallat Unit", "Kallat Plot")
