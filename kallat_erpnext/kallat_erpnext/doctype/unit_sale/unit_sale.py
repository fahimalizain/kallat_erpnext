# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from datetime import datetime
from typing import List, Union
import frappe

# import frappe
# from frappe.model.document import Document
from frappe.utils import flt

from .notification import UnitSaleNotificationHandler
from kallat_erpnext.kallat_erpnext import UnitSaleEventType, UnitSaleStatus, UnitWorkStatus


class UnitSale(UnitSaleNotificationHandler):

    date_time: Union[str, datetime]
    project: str
    plot: str
    unit_type: str
    status: str
    work_status: str
    extra_work: List[dict]
    total_extra_work: float
    agreement_price: float
    total_price: float
    total_percent_due: float

    def validate(self):
        self.validate_plot()
        self.validate_unit_type()
        self.calculate_suggested_price()

    def before_update_after_submit(self):
        self.update_due_and_received()

    def before_submit(self):
        self.status = None
        self.update_due_and_received()

    def validate_plot(self):
        """
        Plot should be of the same project
        """
        plot = frappe.get_doc("Kallat Plot", self.plot)
        if plot.project != self.project:
            frappe.throw(f"Plot {plot.title} do not belong to project {self.project}")

    def validate_unit_type(self):
        """
        Unit Type should be of the same project
        """
        unit_type = frappe.get_doc("Kallat Unit Type", self.unit_type)
        if unit_type.project != self.project:
            frappe.throw(f"UnitType {unit_type.title} do not belong to project {self.project}")

    def calculate_suggested_price(self):
        """
        Suggested Price is calculated only when it is empty
        """
        self.suggested_price = flt(self.suggested_price, 2)
        if self.suggested_price > 0:
            # Entered manually by User or already exists
            return

        plot_price = frappe.db.get_value("Kallat Plot", self.plot, "price")
        unit_type_price = frappe.db.get_value("Kallat Unit Type", self.unit_type, "price")
        self.suggested_price = flt(
            flt(plot_price) + flt(unit_type_price), 2)

    def update_due_and_received(self):
        events = frappe.get_all(
            "Unit Sale Event", {
                "unit_sale": self.name, "docstatus": 1}, [
                "amount_received", "amount_due", "percent_due"])

        self.total_extra_work = flt(sum(x.amount for x in self.extra_work), precision=2)
        self.total_price = flt(
            (self.agreement_price or self.suggested_price) +
            self.total_extra_work + flt(self.total_fine),
            precision=2)

        self.total_percent_due = flt(sum(x.percent_due for x in events), precision=2)
        self.total_due = flt(sum(x.amount_due for x in events), precision=2)
        self.total_received = flt(sum(x.amount_received for x in events), precision=2)
        self.balance_due = max(0, flt(self.total_due - self.total_received))

        self.total_balance = flt(self.total_price - self.total_received, precision=2)

    @frappe.whitelist()
    def get_events(self):
        return frappe.get_all("Unit Sale Event", {
            "docstatus": 1, "unit_sale": self.name,
        }, ["*"], order_by="date_time asc") or []

    @frappe.whitelist()
    def make_payment_receipt(self, amount_received, remarks=None, **kwargs):
        event_doc = frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.PAYMENT_RECEIPT.value,
            unit_sale=self.name,
            remarks=remarks,
            amount_received=amount_received,
            docstatus=1,
            creation=kwargs.get("event_datetime", None),
        ))
        event_doc.insert(ignore_permissions=True)
        self.link_event_files(event_doc, kwargs)
        self.reload()

        # Trigger Payment Receipt Notifications
        self.send_notification(
            self.UNIT_SALE_PAYMENT_RECEIPT,
            context=self.get_context(),
            recipients=self.get_customer_recipients(channels=self.DEFAULT_CHANNELS)
        )

    @frappe.whitelist()
    def confirm_booking(self, event_datetime=None, **kwargs):
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.BOOKED.value,
            unit_sale=self.name,
            remarks="Unit Booked",
            docstatus=1,
            creation=event_datetime or None,
        )).insert(ignore_permissions=True)
        self.reload()

    @frappe.whitelist()
    def sign_agreement(self, agreement_price, agreement_file=None, remarks=None, **kwargs):
        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.AGREEMENT_SIGNED.value,
            unit_sale=self.name,
            remarks=remarks,
            docstatus=1,
            creation=kwargs.get("event_datetime", None),
            misc=frappe.as_json(dict(
                agreement_file=agreement_file,
                agreement_price=flt(agreement_price, precision=2)
            ))
        )).insert(ignore_permissions=True)
        self.reload()

    @frappe.whitelist()
    def update_work_status(self, new_status: str, remarks=None, **kwargs):
        event_doc = frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.WORK_STATUS_UPDATE.value,
            new_status=UnitWorkStatus(new_status).value,
            unit_sale=self.name,
            remarks=remarks,
            docstatus=1,
            creation=kwargs.get("event_datetime", None),
        )).insert(ignore_permissions=True)
        self.link_event_files(event_doc, kwargs)
        self.reload()

        # Trigger WorkStatus Updated Notifications
        self.send_notification(
            self.UNIT_SALE_WORK_STATUS_UPDATED,
            context=self.get_context(),
            recipients=self.get_customer_recipients(channels=self.DEFAULT_CHANNELS)
        )

    @frappe.whitelist()
    def hand_over_unit(self, remarks=None, **kwargs):
        event_doc = frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.UNIT_SALE_UPDATE.value,
            new_status=UnitSaleStatus.HANDED_OVER.value,
            unit_sale=self.name,
            remarks=remarks,
            docstatus=1,
            creation=kwargs.get("event_datetime", None),
        )).insert(ignore_permissions=True)
        self.link_event_files(event_doc, kwargs)
        self.reload()

    @frappe.whitelist()
    def add_extra_work(self, args: dict):
        remarks = args.get("remarks")
        extra_work = args.get("extra_work")

        frappe.get_doc(dict(
            doctype="Unit Sale Event",
            type=UnitSaleEventType.ADD_EXTRA_WORK.value,
            extra_work=[
                dict(
                    title=x.get("title"),
                    qty=x.get("qty"),
                    rate=x.get("rate"),
                    description=x.get("description"))
                for x in extra_work
            ],
            unit_sale=self.name,
            remarks=remarks,
            docstatus=1,
            creation=args.get("event_datetime", None),
        )).insert(ignore_permissions=True)
        self.reload()

    def link_event_files(self, event_doc, files):
        if not files or "num_files" not in files:
            return

        num_files = files.get("num_files")
        file_urls = set()
        for i in range(1, num_files + 1):
            k = f"file_{i}"
            if k not in files:
                continue
            file_urls.add(files.get(k))

        for file_url in file_urls:
            file = frappe.db.get_value("File", {"file_url": file_url})
            frappe.db.set_value(
                "File",
                file,
                dict(
                    attached_to_doctype="Unit Sale Event",
                    attached_to_name=event_doc.name,
                )
            )
