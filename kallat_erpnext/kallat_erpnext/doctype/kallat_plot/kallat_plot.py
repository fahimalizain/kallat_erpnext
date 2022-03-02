# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import cint
from kallat_erpnext.kallat_erpnext import KallatPlotStatus


class KallatPlot(Document):
    def validate(self):
        self.validate_status_change()

    def validate_status_change(self):
        statuses = [e.value for e in KallatPlotStatus]
        if self.status not in statuses:
            raise Exception("Invalid Status")

        if self.is_new():
            return

        if self.get_db_value("status") == self.status:
            # No change to status
            return

        if not cint(self.flags.status_updated):
            raise Exception("Invalid Op")

    @frappe.whitelist()
    def get_unit_sale(self):
        return frappe.db.get_value("Unit Sale", {"docstatus": 1, "unit": self.name})
