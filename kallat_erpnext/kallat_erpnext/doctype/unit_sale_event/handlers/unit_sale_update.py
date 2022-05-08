from typing import TYPE_CHECKING

import frappe
from frappe.utils import flt

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    KallatPlotStatus,
    UnitWorkStatus,
)

if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent


def on_booking(event_doc: "UnitSaleEvent"):
    """
    Invoked when a UnitSale is submitted
    """
    unit_sale = event_doc.unit_sale_doc

    # On Booking, 2.5L is due & is received
    from . import make_due
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

    from . import make_due
    make_due(event_doc)

    event_doc.update_plot_status(KallatPlotStatus.WIP)


def on_handing_over(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc

    from . import make_due
    make_due(event_doc)

    unit_status = UnitSaleStatus(event_doc.new_status)
    event_doc.old_status = unit_sale.status
    unit_sale.update(dict(
        status=unit_status.value
    ))
