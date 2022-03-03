from typing import TYPE_CHECKING
from collections import OrderedDict

import frappe
from frappe.utils import flt, fmt_money

from kallat_erpnext.kallat_erpnext import (
    UnitSaleEventType,
    UnitWorkStatus,
    UnitSaleStatus,
    KallatPlotStatus)

if TYPE_CHECKING:
    from .unit_sale_event import UnitSaleEvent


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
            amt = flt(unit_sale.final_price * schedule.percent / 100, precision=2)

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

    if schedule.upfront:
        total_due = unit_sale.total_due + amount
        total_received = unit_sale.total_received
        if total_due > total_received:
            amt = fmt_money(total_due - total_received, currency="INR")
            msg = f"Please collect upfront payment: {amt}"
            if schedule.type == "Percent":
                msg += f" ({schedule.percent}%)"
            frappe.throw(msg)


def on_booking(event_doc: "UnitSaleEvent"):
    """
    Invoked when a UnitSale is submitted
    """
    unit_sale = event_doc.unit_sale_doc

    # On Booking, 2.5L is due & is received
    make_due(event_doc)

    event_doc.old_status = unit_sale.status
    event_doc.update_plot_status(KallatPlotStatus.BOOKED)
    unit_sale.update(dict(
        status=UnitSaleStatus.BOOKED.value,
        work_status=UnitWorkStatus.NOT_STARTED.value
    ))


def on_signing_agreement(event_doc: "UnitSaleEvent"):
    info = frappe.parse_json(event_doc.misc)
    info.final_price = flt(info.final_price, precision=2)

    unit_sale = event_doc.unit_sale_doc
    event_doc.old_status = unit_sale.status
    unit_sale.update(dict(
        status=UnitSaleStatus.WIP.value,
        final_price=info.final_price,
        agreement_file=info.agreement_file
    ))

    make_due(event_doc)

    event_doc.update_plot_status(KallatPlotStatus.WIP)


def on_handing_over(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc

    make_due(event_doc)

    unit_status = UnitSaleStatus(event_doc.new_status)
    event_doc.old_status = unit_sale.status
    unit_sale.update(dict(
        status=unit_status.value
    ))


def on_work_status_update_up(event_doc: "UnitSaleEvent"):
    make_due(event_doc)
    unit_sale = event_doc.unit_sale_doc

    work_status = UnitWorkStatus(event_doc.new_status)
    if work_status == UnitWorkStatus.FOUNDATION_COMPLETED:
        event_doc.update_plot_status(KallatPlotStatus.WIP)

    event_doc.old_status = unit_sale.work_status
    unit_sale.update(dict(
        work_status=work_status.value
    ))


def on_work_status_update_down(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    if unit_sale.work_status != event_doc.new_status:
        frappe.throw("Please cancel other WorkUpdates made after this")

    unit_sale.update(dict(
        work_status=UnitWorkStatus(event_doc.old_status).value
    ))


def on_payment_receipt_up(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    amount_received = event_doc.amount_received
    if amount_received > unit_sale.total_balance:
        frappe.throw("Cannot receive more than the Total Balance left")

    unit_sale_status = UnitSaleStatus(unit_sale.status or "")
    if amount_received == unit_sale.total_balance and \
            unit_sale_status == UnitSaleStatus.HANDED_OVER:
        # Complete
        on_completion_up(event_doc=event_doc)


def on_payment_receipt_down(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    unit_sale_status = UnitSaleStatus(unit_sale.status or "")

    if unit_sale_status == UnitSaleStatus.COMPLETED and unit_sale.total_balance == 0:
        on_completion_down(event_doc=event_doc)


def on_completion_up(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    unit_sale.status = UnitSaleStatus.COMPLETED.value
    event_doc.update_plot_status(KallatPlotStatus.COMPLETED)


def on_completion_down(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    unit_sale.status = UnitSaleStatus.HANDED_OVER.value
    event_doc.update_plot_status(KallatPlotStatus.WIP)
