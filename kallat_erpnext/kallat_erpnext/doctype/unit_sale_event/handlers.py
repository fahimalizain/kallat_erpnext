from typing import TYPE_CHECKING

import frappe

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
