# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ExtraWorkItem(Document):
    title: str
    status: str
    qty: float
    rate: float
    amount: float
    total_received: float
    description: str
    ref: str
