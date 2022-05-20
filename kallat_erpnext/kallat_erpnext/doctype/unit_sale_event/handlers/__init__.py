from typing import TYPE_CHECKING
from collections import OrderedDict

import frappe
from frappe.utils import flt, fmt_money

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    UnitWorkStatus,
    UnitSaleEventType,
)
if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent

from .payment_receipt import on_payment_receipt_down, on_payment_receipt_up  # noqa
from .work_status_update import on_work_status_update_down, on_work_status_update_up  # noqa
from .unit_sale_update import on_booking, on_handing_over, on_signing_agreement  # noqa
from .extra_work import on_extra_work_up, on_extra_work_down  # noqa

PAYMENT_SCHEDULE = OrderedDict()
PAYMENT_SCHEDULE[UnitSaleStatus.BOOKED] = frappe._dict(
    type="Fixed", amount=250000, remarks="Booking Fee", upfront=True,
)
PAYMENT_SCHEDULE[UnitSaleStatus.AGREEMENT_SIGNED] = frappe._dict(
    type="Percent", percent=40, including_existing_due=True, upfront=True
)
PAYMENT_SCHEDULE[UnitWorkStatus.FOUNDATION_COMPLETED] = frappe._dict(
    type="Percent", percent=30,
)
PAYMENT_SCHEDULE[UnitWorkStatus.FIRST_FLOOR_SLAB_COMPLETED] = frappe._dict(
    type="Percent", percent=20,
)
PAYMENT_SCHEDULE[UnitWorkStatus.STRUCTURE_COMPLETED] = frappe._dict(
    type="Percent", percent=5,
)
PAYMENT_SCHEDULE[UnitWorkStatus.TILING_COMPLETED] = frappe._dict(
    type="Percent", percent=3
)
PAYMENT_SCHEDULE[UnitSaleStatus.HANDED_OVER] = frappe._dict(
    type="Percent", percent=2)


def make_due(event_doc: "UnitSaleEvent"):
    _type = UnitSaleEventType(event_doc.type)
    if _type == UnitSaleEventType.UNIT_SALE_UPDATE:
        _status = UnitSaleStatus(event_doc.new_status)
    elif _type == UnitSaleEventType.WORK_STATUS_UPDATE:
        _status = UnitWorkStatus(event_doc.new_status)
    else:
        return

    if _status not in PAYMENT_SCHEDULE:
        return

    schedule = PAYMENT_SCHEDULE.get(_status)
    unit_sale = event_doc.unit_sale_doc

    def _get_schedule_due_amt(schedule, existing_due=0):
        amt = 0
        if schedule.type == "Fixed":
            amt = schedule.amount
        elif schedule.type == "Percent":
            amt = flt(unit_sale.total_price * schedule.percent / 100, precision=2)

        if schedule.including_existing_due:
            amt = amt - existing_due

        return amt

    # Validate Prev. Dues paid
    prev_due = 0
    for status, _schedule in PAYMENT_SCHEDULE.items():
        if status == _status:
            break

        prev_due += _get_schedule_due_amt(_schedule, existing_due=prev_due)

    if unit_sale.total_received < prev_due:
        frappe.throw(
            "Please make receipts for previous due amount first. Pending Amt: " +
            fmt_money(prev_due - unit_sale.total_received, currency="INR"))

    # Good to go
    # Lets make this schedule due
    amount = _get_schedule_due_amt(schedule, existing_due=unit_sale.total_due)

    amount = flt(amount, precision=2)
    event_doc.amount_due = amount
    event_doc.percent_due = schedule.percent or 0

    if schedule.upfront:
        total_due = unit_sale.total_due + amount
        total_received = unit_sale.total_received
        if total_due > total_received:
            amt = fmt_money(total_due - total_received, currency="INR")
            msg = f"Please collect upfront payment: {amt}"
            if schedule.type == "Percent":
                msg += f" ({schedule.percent}%)"
            frappe.throw(msg)
