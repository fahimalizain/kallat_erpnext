from typing import List

import frappe
from frappe.utils import flt

from kallat_erpnext.kallat_erpnext import UnitSaleEventType
from kallat_erpnext.utils.notification_handler import NotificationScheduleStatus

from .unit_sale import UnitSale


def group_payments(events: List[dict]):
    """
    Groups Each UnitSale of PaymentReceipts into a single Entry

    Incoming events is ordered by date_time desc
    """
    _len_events = len(events)
    for i in range(_len_events):
        i = _len_events - i - 1  # Loop in reverse
        if i <= 0:
            continue

        curr_event = events[i]
        next_event = events[i - 1]

        if curr_event.type != next_event.type:
            continue

        if curr_event.type != UnitSaleEventType.PAYMENT_RECEIPT.value:
            continue

        # Ok, let merge now.
        next_event.amount_received = flt(next_event.amount_received, 2) + \
            flt(curr_event.amount_received, 2)

        next_event.grouped_payments = [next_event.name] + \
            curr_event.get("grouped_payments", [curr_event.name])

        events.pop(i)


def add_notifications(unit_sale: UnitSale, events: List[dict]):
    """
    Inserts Notification Events into the existing list of events
    """

    notifications = frappe.get_all(
        "Kallat Notification Schedule",
        fields=["sent_on", "template_key", "context", "recipients", "name"],
        filters=dict(
            status=NotificationScheduleStatus.SENT.value,
            ref_dt=unit_sale.doctype,
            ref_dn=unit_sale.name))

    events.extend(
        frappe._dict(
            type="Notification",
            template_key=x.template_key,
            date_time=x.sent_on,
            channels=set([c.get("channel") for c in frappe.parse_json(x.recipients or "[]")]),
            name=x.name,
        )
        for x in notifications)

    return sorted(events, key=lambda x: x.get("date_time"), reverse=True)


def get_scheduled_notifications(unit_sale: UnitSale):
    return [
        dict(
            **x,
            type="Notification",
            channels=set([c.get("channel") for c in frappe.parse_json(x.recipients or "[]")]),
            date_time=x.get("scheduled_date_time"),
        )
        for x in frappe.get_all(
            "Kallat Notification Schedule",
            fields=["scheduled_date_time", "template_key", "context", "recipients", "name"],
            filters=dict(
                status=NotificationScheduleStatus.SCHEDULED.value,
                ref_dt=unit_sale.doctype,
                ref_dn=unit_sale.name))]
