from typing import TYPE_CHECKING

import frappe
from kallat_erpnext.kallat_erpnext import (
    UnitWorkStatus,
    KallatPlotStatus,
)

if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent


def on_work_status_update_up(event_doc: "UnitSaleEvent"):
    from . import make_due
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
