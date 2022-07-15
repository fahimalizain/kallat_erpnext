# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from datetime import date
from typing import List, Union

import frappe
from frappe.model.document import Document
from frappe.utils.data import flt

from kallat_erpnext.kallat_accounts.doctype.expense_entry_item.expense_entry_item import \
    ExpenseEntryItem


class ExpenseEntry(Document):

    posting_date: Union[date, str]
    credit_account: str
    items: List[ExpenseEntryItem]
    total_amount: float
    journal_entry: str
    remarks: str

    def validate(self):
        self.validate_items()

    def on_submit(self):
        self.make_journal_entry()

    def before_cancel(self):
        self.ignore_linked_doctypes = ["GL Entry", "Journal Entry"]

    def on_cancel(self):
        self.cancel_journal_entry()

    def validate_items(self):
        total = 0

        expense_types = list(set(x.expense_type for x in self.items))
        for i in range(len(self.items) - 1, -1, -1):
            item = self.items[i]
            if item.expense_type in expense_types:
                expense_types.remove(item.expense_type)
            else:
                self.items.remove(item)

            item.amount = max(0, flt(item.amount, item.precision("amount")))
            total += item.amount

        self.total_amount = flt(total, self.precision("total_amount"))

    def make_journal_entry(self):
        je = frappe.new_doc("Journal Entry")
        je.update(dict(
            posting_date=self.posting_date,
            remark=self.remarks,
        ))

        je.append("accounts", dict(
            account=self.credit_account,
            credit_in_account_currency=self.total_amount,
            reference_type=self.doctype,
            reference_name=self.name,
        ))

        for item in self.items:
            je.append("accounts", dict(
                account=item.expense_account,
                debit_in_account_currency=item.amount,
                reference_type=self.doctype,
                reference_name=self.name,
            ))

        je.docstatus = 1
        je.insert(ignore_permissions=True)
        self.db_set("journal_entry", je.name)

    def cancel_journal_entry(self):
        if not frappe.db.exists("Journal Entry", self.journal_entry):
            return

        je = frappe.get_doc("Journal Entry", self.journal_entry)
        if je.docstatus == 1:
            je.docstatus = 2
            je.save(ignore_permissions=True)
