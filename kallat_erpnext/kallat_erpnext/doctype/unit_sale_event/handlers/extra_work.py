from typing import TYPE_CHECKING

import frappe
from frappe.utils import flt, fmt_money

from kallat_erpnext.kallat_erpnext import UnitSaleExtraWorkStatus
from ...extra_work_item.extra_work_item import ExtraWorkItem

if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent


def on_extra_work_add_up(event_doc: "UnitSaleEvent"):
    """
    Invoked when ExtraWorkItem is being added
    """
    unit_sale = event_doc.unit_sale_doc
    if not len(event_doc.extra_work):
        frappe.throw("Please define Extra Work line items")

    for w in event_doc.extra_work:
        w.amount = flt(flt(w.get("rate")) * flt(w.get("qty")), 2)

        unit_sale.append("extra_work", dict(
            title=w.get("title"),
            description=w.get("description"),
            status=w.get("status"),
            qty=w.get("qty"),
            rate=w.get("rate"),
            amount=w.get("amount"),
            ref=w.get("name"),
        ))


def on_extra_work_add_down(event_doc: "UnitSaleEvent"):
    """
    Invoked when UnitSaleEvent that appended ExtraWorkItem is being Cancelled
    """
    unit_sale = event_doc.unit_sale_doc
    _refs = [x.name for x in event_doc.extra_work]

    unit_sale.extra_work = [
        x for x in unit_sale.extra_work if x.ref not in _refs
    ]


def on_extra_work_update_up(event_doc: "UnitSaleEvent"):
    """
    General ExtraWorkItem Update Handler
    Sub Handlers will be triggered from here.
    """

    args = _get_extra_work_update_args(event_doc)
    extra_work = _get_extra_work_row(event_doc, args.extra_work_row)

    if args.update_type not in _UPDATE_HANDLERS:
        raise Exception("Invalid Update Type: {}".format(args.update_type))

    handler = _UPDATE_HANDLERS[args.update_type]
    handler.up(event_doc=event_doc, extra_work=extra_work, args=args)


def on_extra_work_update_down(event_doc: "UnitSaleEvent"):
    """
    General ExtraWorkItem Update-Down Handler
    Sub Handlers will be triggered from here.
    """
    args = _get_extra_work_update_args(event_doc)
    extra_work = _get_extra_work_row(event_doc, args.extra_work_row)

    if args.update_type not in _UPDATE_HANDLERS:
        raise Exception("Invalid Update Type: {}".format(args.update_type))

    handler = _UPDATE_HANDLERS[args.update_type]
    handler.down(event_doc=event_doc, extra_work=extra_work, args=args)


def _get_extra_work_update_args(event_doc: "UnitSaleEvent"):
    """
    Parse the UnitSaleEvent.misc JSON
    """
    return frappe._dict(frappe.parse_json(event_doc.misc))


def _get_extra_work_row(event_doc: "UnitSaleEvent", extra_work_row: str) -> ExtraWorkItem:
    """
    Get ExtraWorkItem Row Document from UnitSale based on the name given
    :extra_work_row (str): The name of the ExtraWorkItem Row
    """
    unit_sale = event_doc.unit_sale_doc
    return unit_sale.getone("extra_work", {"name": extra_work_row})


def payment_receipt_up(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's Payment Receipt
    """
    # Validate Current status is Pending
    if extra_work.status != UnitSaleExtraWorkStatus.PENDING.value:
        frappe.throw(
            "Cannot make payment against non-pending ExtraWorkItem: {}".format(extra_work.title))

    extra_work.total_received = flt(extra_work.total_received or 0) + \
        abs(flt(args.amount, precision=2))

    # Validate the Amount Received till date
    if extra_work.total_received > extra_work.amount:
        frappe.throw("Cannot receive more than {}".format(fmt_money(extra_work.amount)))

    # Update status if Payment Complete
    if extra_work.total_received == extra_work.amount:
        extra_work.status = UnitSaleExtraWorkStatus.PAYMENT_RECEIVED.value


def payment_receipt_down(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's Payment Receipt (Down Handler)
    """

    if extra_work.status not in (
            UnitSaleExtraWorkStatus.PAYMENT_RECEIVED.value,
            UnitSaleExtraWorkStatus.PENDING.value):
        frappe.throw("Please cancel other Updates on the same ExtraWork first")

    extra_work.total_received -= abs(flt(args.amount, precision=2))
    extra_work.total_received = max(0, extra_work.total_received)
    extra_work.status = UnitSaleExtraWorkStatus.PENDING.value


def start_work_up(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's StartWork Update
    """
    if extra_work.status != UnitSaleExtraWorkStatus.PAYMENT_RECEIVED.value:
        frappe.throw("Cannot start work at this state for ExtraWork: {}".format(extra_work.title))

    extra_work.status = UnitSaleExtraWorkStatus.WORK_IN_PROGRESS.value


def start_work_down(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's StartWork Update (Down Handler)
    """
    if extra_work.status != UnitSaleExtraWorkStatus.WORK_IN_PROGRESS.value:
        frappe.throw("Cannot cancel at this state for ExtraWork: {}".format(extra_work.title))

    extra_work.status = UnitSaleExtraWorkStatus.PAYMENT_RECEIVED.value


def complete_work_up(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's Completion
    """
    if extra_work.status != UnitSaleExtraWorkStatus.WORK_IN_PROGRESS.value:
        frappe.throw("Cannot update work at this state for ExtraWork: {}".format(extra_work.title))

    extra_work.status = UnitSaleExtraWorkStatus.COMPLETED.value


def complete_work_down(event_doc: "UnitSaleEvent", extra_work: ExtraWorkItem, args: dict):
    """
    Invoked on ExtraWork's Completion (Down Handler)
    """
    if extra_work.status != UnitSaleExtraWorkStatus.COMPLETED.value:
        frappe.throw("Cannot cancel at this state for ExtraWork: {}".format(extra_work.title))

    extra_work.status = UnitSaleExtraWorkStatus.WORK_IN_PROGRESS.value


_UPDATE_HANDLERS = frappe._dict(
    PAYMENT_RECEIPT=frappe._dict(
        up=payment_receipt_up, down=payment_receipt_down,
    ),
    START_WORK=frappe._dict(
        up=start_work_up, down=start_work_down,
    ),
    COMPLETE_WORK=frappe._dict(
        up=complete_work_up, down=complete_work_down,
    ),
)
