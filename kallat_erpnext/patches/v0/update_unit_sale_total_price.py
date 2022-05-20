import frappe
from kallat_erpnext.kallat_erpnext.doctype.unit_sale_event.handlers import PAYMENT_SCHEDULE
from kallat_erpnext.kallat_erpnext import (
    UnitSaleEventType,
    UnitWorkStatus,
    UnitSaleStatus
)


def execute():
    frappe.reload_doc("kallat_erpnext", "doctype", "extra_work_item")
    frappe.reload_doctype("Unit Sale")
    frappe.reload_doctype("Unit Sale Event")

    update_unit_sale_event_amount_dues()

    # Update final_price --> agreement_price
    frappe.db.sql("""
    UPDATE `tabUnit Sale` SET agreement_price = final_price
    """)

    for sale in frappe.get_all("Unit Sale", {"docstatus": 1}):
        sale = frappe.get_doc("Unit Sale", sale.name)
        sale.total_price = sale.agreement_price
        sale.flags.ignore_validate_update_after_submit = True
        sale.save(ignore_permissions=True, )

    frappe.db.commit()


def update_unit_sale_event_amount_dues():
    PAYMENT_SCHEDULE
    for event in frappe.get_all("Unit Sale Event", ["name"]):
        event_doc = frappe.get_doc("Unit Sale Event", event.name)

        _type = UnitSaleEventType(event_doc.type)
        if _type == UnitSaleEventType.UNIT_SALE_UPDATE:
            _status = UnitSaleStatus(event_doc.new_status)
        elif _type == UnitSaleEventType.WORK_STATUS_UPDATE:
            _status = UnitWorkStatus(event_doc.new_status)
        else:
            continue

        if _status not in PAYMENT_SCHEDULE:
            continue

        event_doc.db_set(
            "percent_due",
            PAYMENT_SCHEDULE.get(_status).percent or 0)
