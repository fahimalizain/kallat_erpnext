from typing import List

from frappe.utils import flt
from kallat_erpnext.kallat_erpnext import UnitSaleEventType


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
