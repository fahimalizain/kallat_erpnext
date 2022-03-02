from typing import TYPE_CHECKING

import frappe

from kallat_erpnext.kallat_erpnext import (UnitWorkStatus, UnitSaleStatus, KallatPlotStatus)

if TYPE_CHECKING:
    from .unit_sale_event import UnitSaleEvent


def on_booking(event_doc: "UnitSaleEvent"):
    """
    Invoked when a UnitSale is submitted
    """
    # On Booking, 2.5L is due & is received
    event_doc.update_plot_status(KallatPlotStatus.BOOKED)
    event_doc.amount_due = 250000
    event_doc.amount_received = 250000
    event_doc.flags.ignore_validate_update_after_submit = True
    event_doc.save()

    unit_sale = frappe.get_doc("Unit Sale", event_doc.unit_sale)
    unit_sale.update(dict(
        status=UnitSaleStatus.BOOKED.value,
        work_status=UnitWorkStatus.NOT_STARTED.value
    ))
    unit_sale.flags.ignore_validate_update_after_submit = True
    unit_sale.save(ignore_permissions=True)
