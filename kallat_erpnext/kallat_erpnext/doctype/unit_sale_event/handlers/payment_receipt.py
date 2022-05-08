from typing import TYPE_CHECKING

import frappe
from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    KallatPlotStatus,
)

if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent


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
