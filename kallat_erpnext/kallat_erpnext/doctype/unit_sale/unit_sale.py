# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from enum import Enum
import frappe

# import frappe
from frappe.utils import flt
from frappe.model.document import Document
from kallat_erpnext.kallat_erpnext.doctype.kallat_unit.kallat_unit import KallatUnitStatus


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
        KallatUnitStatus.FOUNDATION_COMPLETED: frappe._dict(
            type="Percent", percent=30,
        ),
        KallatUnitStatus.FIRST_FLOOR_SLAB_COMPLETED: frappe._dict(
            type="Percent", percent=20,
        ),
        KallatUnitStatus.STRUCTURE_COMPLETED: frappe._dict(
            type="Percent", percent=5,
        ),
        KallatUnitStatus.TILING_COMPLETED: frappe._dict(
            type="Percent", percent=3
        ),
        KallatUnitStatus.HAND_OVER_COMPLETED: frappe._dict(
            type="Percent", percent=2
        )
    }
)


class UnitSale(Document):
    def validate(self):
        self.validate_unit()

    def before_submit(self):
        self.schedule_due_payment(
            new_status=UnitSaleStatuses(self.status)
        )

    def validate_unit(self):
        unit = frappe.get_doc("Kallat Unit", self.unit)
        if unit.project != self.project:
            frappe.throw(f"Unit {unit.title} do not belong to project {self.project}")

        self.unit_price = unit.price

    def update_unit_status(self):
        unit_status = frappe.db.get_value("Kallat Unit", self.unit, "status")
        self.unit_status = unit_status

    def update_amount_due(self):
        self.total_due = flt(sum(x.amount for x in self.scheduled_payments), precision=2)

    def schedule_due_payment(self, new_status, remarks=None):
        if new_status not in PAYMENT_SCHEDULE:
            return

        schedule = PAYMENT_SCHEDULE.get(new_status)
        amount = 0
        if schedule.type == "Fixed":
            amount = schedule.amount
        elif schedule.type == "Percent":
            amount = self.unit_price * schedule.percent / 100

        amount = flt(amount, precision=2)

        self.append("scheduled_payments", dict(
            remarks=remarks or schedule.get("remarks"),
            type=schedule.get("type"),
            percentage=schedule.get("percent"),
            amount=amount
        ))
        self.update_amount_due()
