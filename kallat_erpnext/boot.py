import frappe


def boot_session(boot):
    # This will control if the fields on UnitSale Forms's creation
    # field will be ReadOnly or not
    boot.kallat_modify_timestamp = bool(frappe.conf.kallat_modify_timestamp)
