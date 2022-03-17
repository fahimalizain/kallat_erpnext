

def daily():
    from kallat_erpnext.kallat_erpnext.doctype.unit_sale.late_fines import check_late_fines
    check_late_fines()
