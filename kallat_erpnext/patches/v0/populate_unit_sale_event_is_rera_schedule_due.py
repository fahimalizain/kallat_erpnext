import frappe
from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    UnitWorkStatus,
    UnitSaleEventType,
)
from kallat_erpnext.kallat_erpnext.doctype.unit_sale_event.handlers import PAYMENT_SCHEDULE


def execute():
    frappe.reload_doctype("Unit Sale Event")
    dt = "Unit Sale Event"
    events = frappe.get_all(
        dt,
        fields=["name", "type", "new_status"],
        filters=dict(
            docstatus=1,
        )
    )

    for event in events:
        _type = UnitSaleEventType(event.type)
        if _type == UnitSaleEventType.UNIT_SALE_UPDATE:
            _status = UnitSaleStatus(event.new_status)
        elif _type == UnitSaleEventType.WORK_STATUS_UPDATE:
            _status = UnitWorkStatus(event.new_status)
        else:
            continue

        if _status not in PAYMENT_SCHEDULE:
            continue

        frappe.db.set_value(dt, event.name, "is_rera_schedule_due", 1)
