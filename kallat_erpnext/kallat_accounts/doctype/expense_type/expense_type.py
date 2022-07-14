# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExpenseType(Document):
    enabled: int
    title: str
    expense_account: str

    def validate(self):
        self.validate_account_type()

    def validate_account_type(self):
        root_type = frappe.db.get_value("Account", self.expense_account, "root_type")
        if root_type != "Expense":
            frappe.throw("Account provided is not an Expense Account")
