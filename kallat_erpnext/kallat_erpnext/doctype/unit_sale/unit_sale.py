# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from enum import Enum
import frappe

# import frappe
from frappe.utils import flt
from frappe.model.document import Document
from kallat_erpnext.kallat_erpnext.doctype.kallat_plot.kallat_plot import KallatPlotStatus


class UnitSaleStatuses(Enum):
    BOOKED = "Booked"
    AGREEMENT_SIGNED = "Agreement Signed"
    WIP = "Work In Progress"
    COMPLETED = "Completed"


PAYMENT_SCHEDULE = frappe._dict(
    {
        UnitSaleStatuses.BOOKED: frappe._dict(
            type="Fixed", amount=250000, remarks="Booking Fee"
        ),
        UnitSaleStatuses.AGREEMENT_SIGNED: frappe._dict(
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


class UnitSale(Document):
    def validate(self):
        self.suggested_price = 0
        self.validate_plot()
        self.validate_unit_type()

        self.suggested_price = flt(self.suggested_price, precision=2)

    def before_submit(self):
        self.schedule_due_payment(
            new_status=UnitSaleStatuses(self.status),
            auto_save=False
        )

    def validate_plot(self):
        plot = frappe.get_doc("Kallat Plot", self.plot)
        if plot.project != self.project:
            frappe.throw(f"Plot {plot.title} do not belong to project {self.project}")

        self.suggested_price += flt(plot.price)

    def validate_unit_type(self):
        unit_type = frappe.get_doc("Kallat Unit Type", self.unit_type)
        if unit_type.project != self.project:
            frappe.throw(f"UnitType {unit_type.title} do not belong to project {self.project}")

        self.suggested_price += flt(unit_type.price)

    def update_plot_status(self):
        self.plot_status = frappe.db.get_value("Kallat Plot", self.plot, "status")

    def calculate_totals(self):
        self.total_due = flt(sum(x.amount for x in self.scheduled_payments), precision=2)
        self.total_received = flt(sum(x.amount for x in self.payments_received), precision=2)
        self.balance_amount = flt(self.unit_price - self.total_received, precision=2)

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

    @frappe.whitelist()
    def sign_agreement(self, agreement_file, remarks=None):
        if UnitSaleStatuses(self.status) != UnitSaleStatuses.BOOKED:
            frappe.throw("Invalid OP")

        file = frappe.db.get_value("File", {"file_url": agreement_file})
        if not file:
            frappe.throw("File not found, Please re-upload ?")

        # Attach file to this Sale
        self.status = UnitSaleStatuses.WIP.value  # Let's start work!
        self.agreement_file = agreement_file
        self.schedule_due_payment(
            new_status=UnitSaleStatuses.AGREEMENT_SIGNED,
            remarks=remarks or "Agreement Signed"
        )
