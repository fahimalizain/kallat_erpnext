from typing import TYPE_CHECKING

import frappe
from frappe.utils import flt, fmt_money

from kallat_erpnext.kallat_erpnext import (UnitWorkStatus, UnitSaleStatus, KallatPlotStatus)

if TYPE_CHECKING:
    from .unit_sale_event import UnitSaleEvent


def on_booking(event_doc: "UnitSaleEvent"):
    """
    Invoked when a UnitSale is submitted
    """
    unit_sale = event_doc.unit_sale_doc
    if unit_sale.total_received < 250000:
        frappe.throw("Please make receipt for 2.5L first")

    # On Booking, 2.5L is due & is received
    event_doc.update_plot_status(KallatPlotStatus.BOOKED)
    event_doc.amount_due = 250000

    unit_sale.update(dict(
        status=UnitSaleStatus.BOOKED.value,
        work_status=UnitWorkStatus.NOT_STARTED.value
    ))


def on_signing_agreement(event_doc: "UnitSaleEvent"):
    info = frappe.parse_json(event_doc.misc)
    info.final_price = flt(info.final_price, precision=2)
    minimum_payment = flt(40 * info.final_price / 100, precision=2)

    unit_sale = event_doc.unit_sale_doc
    if unit_sale.total_received < minimum_payment:
        amt = fmt_money(minimum_payment, currency="INR")
        frappe.throw(f"Please get a minimum of {amt} before signing the Agreement")

    event_doc.amount_due = flt(minimum_payment - unit_sale.total_received, precision=2)

    event_doc.update_plot_status(KallatPlotStatus.WIP)
    unit_sale.update(dict(
        status=UnitSaleStatus.WIP.value,
        final_price=info.final_price
    ))
