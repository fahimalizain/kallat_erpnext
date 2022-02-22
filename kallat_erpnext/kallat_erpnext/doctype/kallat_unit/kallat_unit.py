# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from enum import Enum

import frappe
from frappe.model.document import Document
from frappe.utils import cint, now_datetime


class KallatUnitStatus(Enum):
    EMPTY_PLOT = "Empty Plot"
    FOUNDATION_COMPLETED = "Foundation Completed"
    FIRST_FLOOR_SLAB_COMPLETED = "1st Floor Slab Completed"
    STRUCTURE_COMPLETED = "Structure Completed"
    TILING_COMPLETED = "Tiling Completed"
    HAND_OVER_COMPLETED = "Hand Over Completed"


class KallatUnit(Document):
    def validate(self):
        self.validate_status_change()

    def on_update(self):
        if self.flags.status_updated:
            self.update_unit_sale()

    def validate_status_change(self):
        statuses = [e.value for e in KallatUnitStatus]
        if self.status not in statuses:
            raise Exception("Invalid Status")

        if self.is_new():
            return

        if self.get_db_value("status") == self.status:
            # No change to status
            return

        # There is change, lets make sure Unit Sale exists
        if not self.get_unit_sale():
            frappe.throw("This plot has not been sold yet to start work")

        if not cint(self.flags.status_updated):
            raise Exception("Invalid Op")

    def get_unit_sale(self):
        return frappe.db.get_value("Unit Sale", {"docstatus": 1, "unit": self.name})

    @frappe.whitelist()
    def update_status(self, new_status: str, remarks: str = None):
        self.flags.status_updated = True
        self.append("status_updates", dict(
            date_time=now_datetime(),
            remarks=remarks,
            prev_status=self.status,
            new_status=new_status
        ))
        self.status = new_status
        self.save()

    def update_unit_sale(self):
        unit_sale = frappe.get_doc("Unit Sale", self.get_unit_sale())
        unit_sale.schedule_due_payment(
            new_status=KallatUnitStatus(self.status),
            remarks="Unit status Update",
            auto_save=True
        )
