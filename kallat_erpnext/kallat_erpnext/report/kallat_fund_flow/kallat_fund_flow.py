# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt
from typing import Dict, List
from dateutil import parser

import frappe
from frappe.utils import get_last_day, get_first_day
from frappe.utils.data import flt
from kallat_erpnext.kallat_erpnext import UnitSaleEventType, UnitSaleStatus

"""
Kallat Fund Flow
------------------------------
Param: Month/Year
Columns:
    Name: Name of the Customer
    Villa No: Plot Number ?
    Sq. Ft: The square feet of the plot
    Sale: The total sale amount
    Total Sale 5%: Add 5% to existing Sale value
    Opening Receipt: Sum of money received till prev month of Month/Year
    Current Amount: Money Received in this Month
    Total Received: Opening Receipt + Current Month
    Balance: Total w/ 5% Tax - Total Received
    %: The percentage of amount paid
"""


class SalePaymentReceiptSummary:
    opening_receipt: int
    received_this_month: int
    total_received: int

    def __init__(self) -> None:
        self.opening_receipt = 0
        self.received_this_month = 0
        self.total_received = 0


def execute(filters: dict = None):

    columns, data = get_columns(filters=filters), get_data(filters=filters)
    return columns, data


def get_columns(filters: dict):
    return [
        dict(label="Unit Sale", fieldname="unit_sale", fieldtype="Link", options="Unit Sale"),
        dict(label="Customer", fieldname="customer_name", fieldtype="Data"),
        dict(label="Villa No", fieldname="plot", fieldtype="Data"),
        dict(label="Sq Ft.", fieldname="sq_ft", fieldtype="Float"),
        dict(label="Sale", fieldname="agreement_price", fieldtype="Currency"),
        # dict(label="Sale w/ 5%", fieldname="total_price", fieldtype="Currency"),
        dict(label="Opening Receipt", fieldname="opening_receipt", fieldtype="Currency"),
        dict(label="Current Amount", fieldname="received_this_month", fieldtype="Currency"),
        dict(label="Total Received", fieldname="total_received", fieldtype="Currency"),
        dict(label="Balance", fieldname="balance_amount", fieldtype="Currency"),
        dict(label="%", fieldname="percent_paid", fieldtype="Percent"),
    ]


def get_data(filters: dict):
    data = get_pending_unit_sales(filters)
    receipts = get_payment_summary(filters=filters, unit_sales=[x.unit_sale for x in data])
    update_amounts(data, receipts)

    return data


def get_pending_unit_sales(filters: dict):
    """
    All those Unit Sales that had Booking Confirmation done and is pending Completion
    We join two tables of UnitSaleEvent where we
    have one for Booking Confirmation and the other for Completion
    And take all those which has
    - Completion is in future
    - Completion is NULL, hence still pending
    """
    first_day = get_first_day(parser.parse(f"1 {filters.get('month')} {filters.get('year')}"))
    last_day = get_last_day(first_day)

    return frappe.db.sql("""
    SELECT
        DISTINCT
        event_1.unit_sale,
        customer.customer_name,
        unit_sale.plot,
        unit_sale.agreement_price,
        unit_sale.suggested_price
    FROM `tabUnit Sale Event` event_1
    LEFT JOIN `tabUnit Sale Event` event_2
        ON event_1.unit_sale = event_2.unit_sale
    JOIN `tabUnit Sale` unit_sale
        ON unit_sale.name = event_1.unit_sale
    JOIN `tabCustomer` customer
        ON customer.name = unit_sale.customer
    WHERE
        event_1.docstatus = 1
        AND event_1.type = %(UNIT_SALE_UPDATE)s
        AND event_1.new_status = %(UNIT_SALE_BOOKED)s
        AND event_1.date_time < %(last_day)s
        AND (
            event_2.unit_sale IS NULL
            OR (
                event_2.docstatus = 1
                AND (
                    event_2.new_status != %(UNIT_SALE_COMPLETED)s
                    OR
                    (
                        event_2.type = %(UNIT_SALE_UPDATE)s
                        AND event_2.new_status = %(UNIT_SALE_COMPLETED)s
                        AND event_2.date_time > %(first_day)s
                    )
                )
            )
        )
    """, {
        "UNIT_SALE_UPDATE": UnitSaleEventType.UNIT_SALE_UPDATE.value,
        "UNIT_SALE_BOOKED": UnitSaleStatus.BOOKED.value,
        "UNIT_SALE_COMPLETED": UnitSaleStatus.COMPLETED.value,
        "first_day": first_day,
        "last_day": last_day,
    }, as_dict=1, debug=0)


def get_payment_summary(
        filters: dict, unit_sales: List[str]) -> Dict[str, SalePaymentReceiptSummary]:
    """
    Gets a list of payment receipts made against the provided list of UnitSales
    Before specified time
    """
    if not len(unit_sales):
        return dict()

    last_day = get_last_day(parser.parse(f"1 {filters.get('month')} {filters.get('year')}"))
    first_day = get_first_day(last_day)

    payments = frappe.db.sql("""
    SELECT
        DATE(date_time) as payment_date,
        unit_sale,
        amount_received
    FROM `tabUnit Sale Event`
    WHERE
        docstatus = 1
        AND type = %(PAYMENT_RECEIPT)s
        AND date_time < %(last_day)s
        AND unit_sale IN %(unit_sales)s
    """, {
        "PAYMENT_RECEIPT": UnitSaleEventType.PAYMENT_RECEIPT.value,
        "last_day": last_day,
        "unit_sales": unit_sales,
    }, as_dict=1)

    receipt_map = dict()
    for payment in payments:
        summary: SalePaymentReceiptSummary = receipt_map.setdefault(
            payment.unit_sale, SalePaymentReceiptSummary())
        summary.total_received += payment.amount_received

        if payment.payment_date >= first_day:
            summary.received_this_month += payment.amount_received
        else:
            summary.opening_receipt += payment.amount_received

    return receipt_map


def update_amounts(data: List[dict], receipt_map: Dict[str, SalePaymentReceiptSummary]):
    """
    """
    for row in data:
        payment_summary = receipt_map.get(row.unit_sale)
        if not payment_summary:
            payment_summary = SalePaymentReceiptSummary()

        row.total_received = payment_summary.total_received
        row.opening_receipt = payment_summary.opening_receipt
        row.received_this_month = payment_summary.received_this_month

        row.agreement_price = row.agreement_price or row.suggested_price
        row.balance_amount = row.agreement_price - row.total_received
        row.percent_paid = flt(row.total_received * 100 / row.agreement_price, 2)
