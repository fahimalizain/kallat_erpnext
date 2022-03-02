# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING


import frappe
from frappe.utils import flt, now
from frappe.model.document import Document

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    UnitWorkStatus,
    KallatPlotStatus,
    UnitSaleEventType)
from .handlers import on_booking

if TYPE_CHECKING:
    from kallat_erpnext.kallat_erpnext.doctype.unit_sale.unit_sale import UnitSale

EVENT_HANDLERS = frappe._dict({
    UnitSaleEventType.UNIT_SALE_UPDATE: frappe._dict({
        UnitSaleStatus.BOOKED: on_booking
    })
})


PAYMENT_SCHEDULE = frappe._dict(
    {
        UnitSaleStatus.BOOKED: frappe._dict(
            type="Fixed", amount=250000, remarks="Booking Fee"
        ),
        UnitSaleStatus.AGREEMENT_SIGNED: frappe._dict(
            type="Percent", percent=40, consider_already_paid=True,
        ),
        KallatPlotStatus.FOUNDATION_COMPLETED: frappe._dict(
            type="Percent", percent=30,
        ),
        KallatPlotStatus.FIRST_FLOOR_SLAB_COMPLETED: frappe._dict(
            type="Percent", percent=20,
        ),
        KallatPlotStatus.STRUCTURE_COMPLETED: frappe._dict(
            type="Percent", percent=5,
        ),
        KallatPlotStatus.TILING_COMPLETED: frappe._dict(
            type="Percent", percent=3
        ),
        KallatPlotStatus.HAND_OVER_COMPLETED: frappe._dict(
            type="Percent", percent=2
        )
    }
)


class UnitSaleEvent(Document):

    unit_sale_doc: "UnitSale"

    def validate(self):
        if not self.date_time:
            self.date_time = now()

    def before_submit(self):
        self.unit_sale_doc = frappe.get_doc("Unit Sale", self.unit_sale)

        event_type = UnitSaleEventType(self.type)
        if event_type in EVENT_HANDLERS:
            if event_type == UnitSaleEventType.UNIT_SALE_UPDATE:
                sub_type = UnitSaleStatus(self.new_status)
            elif event_type == UnitSaleEventType.WORK_STATUS_UPDATE:
                sub_type = UnitWorkStatus(self.new_status)

            EVENT_HANDLERS[event_type].get(sub_type, lambda *args, **kwargs: None)(
                event_doc=self
            )

    def on_submit(self):
        self.unit_sale_doc.flags.ignore_validate_update_after_submit = True
        self.unit_sale_doc.save(ignore_permissions=True)

    def get_plot(self):
        return frappe.db.get_value("Unit Sale", self.unit_sale, "plot")

    def update_plot_status(self, new_status: KallatPlotStatus):
        plot = frappe.get_doc("Kallat Plot", self.get_plot())
        plot.flags.status_updated = True
        plot.status = new_status.value
        plot.save(ignore_permissions=True)

    def schedule_due_payment(self, new_status, remarks=None, auto_save=True):
        if new_status not in PAYMENT_SCHEDULE:
            return

        schedule = PAYMENT_SCHEDULE.get(new_status)
        amount = 0
        if schedule.type == "Fixed":
            amount = schedule.amount
        elif schedule.type == "Percent":
            amount = self.unit_price * schedule.percent / 100

        if schedule.consider_already_paid:
            amount = amount - self.total_due

        amount = flt(amount, precision=2)
        self.append("scheduled_payments", dict(
            remarks=remarks or schedule.get("remarks"),
            type=schedule.get("type"),
            percentage=schedule.get("percent"),
            amount=amount
        ))
        self.calculate_totals()
        self.update_plot_status()
        if auto_save:
            self.flags.ignore_validate_update_after_submit = True
            self.save()
