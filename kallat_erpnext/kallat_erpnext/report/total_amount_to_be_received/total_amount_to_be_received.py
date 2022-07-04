# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

import frappe


"""
Total Amount to be Received
---------------------------
On Signed Agreement Sales, amount left to receive from Total.
This is independent of Due Amounts
"""


def execute(filters: dict = None):

    columns, data = get_columns(filters=filters), get_data(filters=filters)
    return columns, data


def get_columns(filters: dict):
    return [
        dict(label="Customer", fieldname="customer", fieldtype="Link", options="Customer"),
        dict(label="Unit Sale", fieldname="unit_sale", fieldtype="Link", options="Unit Sale"),
        dict(label="Plot", fieldname="plot", fieldtype="Link", options="Kallat Plot"),
        dict(label="Type", fieldname="unit_type", fieldtype="Link", options="Kallat Unit Type"),
        dict(label="Status", fieldname="status", fieldtype="Data"),
        dict(label="Total Amount", fieldname="total_price", fieldtype="Currency"),
        dict(label="Total Received", fieldname="total_received", fieldtype="Currency"),
        dict(label="Total Balance", fieldname="total_balance", fieldtype="Currency"),
    ]


def get_data(filters: dict):
    return frappe.db.sql("""
    SELECT
        unit_sale.customer,
        unit_sale.name as unit_sale,
        unit_sale.plot,
        unit_sale.unit_type,
        CONCAT(unit_sale.status, ': ', unit_sale.work_status) as status,
        unit_sale.total_price,
        unit_sale.total_received,
        unit_sale.total_balance
    FROM `tabUnit Sale` unit_sale
    WHERE
        unit_sale.docstatus = 1
        AND unit_sale.status NOT IN ('')
        AND unit_sale.total_balance > 0
    """)
