# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING


import frappe
from frappe.utils import now, get_link_to_form
from frappe.model.document import Document

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus,
    # UnitWorkStatus,
    KallatPlotStatus,
    UnitSaleEventType)
from .handlers import (
    on_payment_receipt_up, on_payment_receipt_down,
    on_booking,
    on_signing_agreement,
    on_handing_over,
    on_work_status_update_up,
    on_work_status_update_down,
    on_extra_work_up,
    on_extra_work_down,
    on_extra_work_update_up,
    on_extra_work_update_down)

if TYPE_CHECKING:
    from kallat_erpnext.kallat_erpnext.doctype.unit_sale.unit_sale import UnitSale

EVENT_HANDLERS = frappe._dict({
    UnitSaleEventType.UNIT_SALE_UPDATE: frappe._dict({
        UnitSaleStatus.BOOKED: on_booking,
        UnitSaleStatus.AGREEMENT_SIGNED: on_signing_agreement,
        UnitSaleStatus.HANDED_OVER: on_handing_over,
    }),
    UnitSaleEventType.WORK_STATUS_UPDATE: dict(
        up=on_work_status_update_up, down=on_work_status_update_down),
    UnitSaleEventType.PAYMENT_RECEIPT: dict(
        up=on_payment_receipt_up, down=on_payment_receipt_down,
    ),
    UnitSaleEventType.ADD_EXTRA_WORK: dict(
        up=on_extra_work_up, down=on_extra_work_down,
    ),
    UnitSaleEventType.EXTRA_WORK_UPDATE: dict(
        up=on_extra_work_update_up, down=on_extra_work_update_down,
    ),
})


class UnitSaleEvent(Document):

    unit_sale_doc: "UnitSale"
    amount_due: float
    percent_due: float
    unit_sale: str
    is_rera_schedule_due: int

    def validate(self):
        self.status = ""  # None status
        if not self.date_time:
            self.date_time = now()

    def before_submit(self):
        self.validate_future_events()
        self.run_handler(for_cancel=False)

    def before_cancel(self):
        self.validate_future_events()
        self.run_handler(for_cancel=True)

    def before_update_after_submit(self):
        self.validate_future_events()

    def on_submit(self):
        self.unit_sale_doc.flags.ignore_validate_update_after_submit = True
        self.unit_sale_doc.save(ignore_permissions=True)

    def on_cancel(self):
        self.unit_sale_doc.flags.ignore_validate_update_after_submit = True
        self.unit_sale_doc.save(ignore_permissions=True)

    def validate_future_events(self):
        """
        - Before Submit
        - On Cancel
        - On Update After Submit

        These are the different Events when this could be invoked. These can be understood
        using self._action
        """
        events = frappe.get_all(
            "Unit Sale Event",
            filters=dict(
                unit_sale=self.unit_sale,
                name=["!=", self.name],
                date_time=[">=", self.date_time]
            ),
            order_by="date_time asc")

        if len(events):
            _action = "cancel" if self._action == "cancel" else "make updates to"
            frappe.throw(frappe._(
                f"You cannot {_action} this event when"
                " there exists future Events like {}").format(
                get_link_to_form(self.doctype, events[0].name)))

    def run_handler(self, for_cancel=False):
        self.unit_sale_doc = frappe.get_doc("Unit Sale", self.unit_sale)
        event_type = UnitSaleEventType(self.type)
        if event_type in EVENT_HANDLERS:
            handler = None
            if event_type == UnitSaleEventType.UNIT_SALE_UPDATE:
                sub_type = UnitSaleStatus(self.new_status)
                handler = EVENT_HANDLERS[event_type].get(sub_type)
            elif event_type in (UnitSaleEventType.WORK_STATUS_UPDATE,
                                UnitSaleEventType.PAYMENT_RECEIPT,
                                UnitSaleEventType.ADD_EXTRA_WORK):
                handler = EVENT_HANDLERS[event_type]

            if isinstance(handler, dict):
                handler = handler.get("up") if not for_cancel else handler.get("down")
            elif for_cancel:
                # For Cancel. No Down Handler provided
                return

            if not handler:
                return

            handler(
                event_doc=self
            )

    def get_plot(self):
        return frappe.db.get_value("Unit Sale", self.unit_sale, "plot")

    def update_plot_status(self, new_status: KallatPlotStatus):
        plot = frappe.get_doc("Kallat Plot", self.get_plot())
        plot.flags.status_updated = True
        plot.status = new_status.value
        plot.save(ignore_permissions=True)
