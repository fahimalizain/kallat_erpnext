from typing import TYPE_CHECKING

import frappe
from frappe.utils import flt

if TYPE_CHECKING:
    from ..unit_sale_event import UnitSaleEvent


def on_extra_work_up(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    if not len(event_doc.extra_work):
        frappe.throw("Please define Extra Work line items")

    for w in event_doc.extra_work:
        w.amount = flt(flt(w.get("rate")) * flt(w.get("qty")), 2)

        unit_sale.append("extra_work", dict(
            title=w.get("title"),
            description=w.get("description"),
            qty=w.get("qty"),
            rate=w.get("rate"),
            amount=w.get("amount"),
            ref=w.get("name"),
        ))


def on_extra_work_down(event_doc: "UnitSaleEvent"):
    unit_sale = event_doc.unit_sale_doc
    _refs = [x.name for x in event_doc.extra_work]

    unit_sale.extra_work = [
        x for x in unit_sale.extra_work if x.ref not in _refs
    ]
