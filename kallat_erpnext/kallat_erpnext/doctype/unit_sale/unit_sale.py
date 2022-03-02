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

    def before_submit(self):
        self.status = None
        self.update_due_and_received()

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
        self.balance_amount = flt((self.final_price or self.suggested_price)
                                  - self.total_received, precision=2)

    @frappe.whitelist()
    def get_events(self):
        return frappe.get_all("Unit Sale Event", {
            "docstatus": 1, "unit_sale": self.name,
        }, ["*"], order_by="creation asc")

    @frappe.whitelist()
    def make_payment_receipt(self, amount_received, remarks=None):
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.PAYMENT_RECEIPT.value,
            unit_sale=self.name,
            remarks=remarks,
            amount_received=amount_received,
            docstatus=1
        )).insert(ignore_permissions=True)
        self.reload()

    @frappe.whitelist()
    def confirm_booking(self):
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.BOOKED.value,
            unit_sale=self.name,
            remarks="Unit Booked",
            docstatus=1
        )).insert(ignore_permissions=True)
        self.reload()

    @frappe.whitelist()
    def sign_agreement(self, agreement_file, final_price, remarks=None):
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.AGREEMENT_SIGNED.value,
            unit_sale=self.name,
            remarks=remarks,
            docstatus=1,
            misc=frappe.as_json(dict(
                agreement_file=agreement_file,
                final_price=flt(final_price, precision=2)
            ))
        )).insert(ignore_permissions=True)
        pass
