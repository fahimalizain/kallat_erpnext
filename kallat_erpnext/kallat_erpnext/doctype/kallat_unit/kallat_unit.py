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

    def validate_status_change(self):
        statuses = [e.value for e in KallatUnitStatus]
        if self.status not in statuses:
            raise Exception("Invalid Status")

        if self.is_new():
            return
        if not cint(self.flags.allow_status_change):
            raise Exception("Invalid Op")

    @frappe.whitelist()
    def update_status(self, new_status: str, remarks: str = None):
        self.flags.allow_status_change = True
        self.append("status_updates", dict(
            date_time=now_datetime(),
            remarks=remarks,
            prev_status=self.status,
            new_status=new_status
        ))
        self.status = new_status
        self.save()
