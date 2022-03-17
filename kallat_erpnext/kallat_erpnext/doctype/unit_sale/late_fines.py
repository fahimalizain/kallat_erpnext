import frappe
from frappe.utils import flt, cint, now_datetime, date_diff, fmt_money

from .unit_sale import UnitSale
from kallat_erpnext.kallat_erpnext import UnitSaleStatus, UnitSaleEventType


def check_late_fines():
    pending_sales = frappe.get_all(
        "Unit Sale",
        filters=dict(
            docstatus=1,
            status=["not in", [UnitSaleStatus.COMPLETED.value]]
        )
    )

    for sale in pending_sales:
        sale = frappe.get_doc("Unit Sale", sale.name)
        check_late_fine(sale)


def check_late_fine(sale: UnitSale):
    if sale.balance_due <= 0:
        return

    recent_due_event_date = get_recent_due_event_date(sale=sale)
    last_fine_date = get_last_fine_date(sale=sale)

    days_since_last_event = date_diff(now_datetime(), recent_due_event_date)
    if days_since_last_event < 7:
        return

    if last_fine_date and date_diff(now_datetime(), last_fine_date) < 7:
        return

    # Ok, so we are have to make a Fine Entry now!
    fine_percentage = cint(days_since_last_event / 7) * 0.5
    fine_amount = flt(sale.balance_due * fine_percentage / 100, precision=2)

    frappe.get_doc(dict(
        doctype="Unit Sale Event",
        type=UnitSaleEventType.LATE_FEE_APPLIED.value,
        unit_sale=sale.name,
        remarks=f"{fine_percentage}% of {fmt_money(sale.balance_due)}",
        misc=frappe.as_json(dict(
            fine_percentage=fine_percentage,
            fine_amount=fine_amount,
            fine_on_due=sale.balance_due
        )),
        docstatus=1,
        amount_due=fine_amount
    )).insert(ignore_permissions=True)


def get_recent_due_event_date(sale: UnitSale):
    recent_due_event = frappe.get_all(
        "Unit Sale Event",
        filters=dict(
            unit_sale=sale.name,
            type=["not in", [UnitSaleEventType.LATE_FEE_APPLIED.value]],
            order_by="date_time desc",
            amount_due=[">", 0]
        ),
        fields=["name", "date_time", "amount_due", "misc"],
        limit_page_length=1
    )

    return recent_due_event.date_time


def get_all_fine_events(sale: UnitSale):
    fine_events = frappe.get_all(
        "Unit Sale Event",
        filters=dict(
            unit_sale=sale.name,
            type=UnitSaleEventType.LATE_FEE_APPLIED.value,
            order_by="date_time asc",
        ),
        fields=["name", "date_time", "amount_due", "misc"]
    )

    return fine_events


def get_last_fine_date(sale: UnitSale):
    events = get_all_fine_events()
    if not len(events):
        return None

    return events[-1].date_time
