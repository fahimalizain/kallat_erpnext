# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

import frappe

# import frappe
from frappe.utils import flt
from frappe.model.document import Document
from kallat_erpnext.kallat_erpnext import UnitSaleEventType, UnitSaleStatus


class UnitSale(Document):
    def validate(self):
        self.suggested_price = 0
        self.validate_plot()
        self.validate_unit_type()

        self.suggested_price = flt(self.suggested_price, precision=2)

    def before_update_after_submit(self):
        self.update_due_and_received()

    def on_submit(self):
        self.status = None
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.BOOKED.value,
            unit_sale=self.name,
            remarks="Unit Booked",
            docstatus=1
        )).insert(ignore_permissions=True)
        self.reload()

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

    def update_due_and_received(self):
        events = frappe.get_all(
            "Unit Sale Event", {
                "unit_sale": self.name, "docstatus": 1}, [
                "amount_received", "amount_due"])
        self.total_due = flt(sum(x.amount_due for x in events), precision=2)
        self.total_received = flt(sum(x.amount_received for x in events), precision=2)
        self.balance_amount = flt(self.unit_price - self.total_received, precision=2)

    @frappe.whitelist()
    def sign_agreement(self, agreement_file, remarks=None):
        # if UnitSaleStatuses(self.status) != UnitSaleStatuses.BOOKED:
        #     frappe.throw("Invalid OP")

        # file = frappe.db.get_value("File", {"file_url": agreement_file})
        # if not file:
        #     frappe.throw("File not found, Please re-upload ?")

        # # Attach file to this Sale
        # self.status = UnitSaleStatuses.WIP.value  # Let's start work!
        # self.agreement_file = agreement_file
        # self.schedule_due_payment(
        #     new_status=UnitSaleStatuses.AGREEMENT_SIGNED,
        #     remarks=remarks or "Agreement Signed"
        # )
        pass
