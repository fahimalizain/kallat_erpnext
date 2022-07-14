# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

import unittest

import frappe
from erpnext import get_default_company

from kallat_erpnext.tests import TestFixture


class ExpenseTypeFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Expense Type"

    def make_fixtures(self):
        sample_types = [
            "Expense Type 1",
            "Expense Type 2",
            "Expense Type 3",
            "Expense Type 4",
            "Expense Type 5",
        ]

        for _type in sample_types:
            self._get_expense_type(_type)

    def _get_expense_type(self, title: str):
        """
        Makes an Expense Account with title, and an Expense Type with the same Title
        """
        expense_acc = self._get_expense_acc(title)

        doc = frappe.new_doc("Expense Type")
        doc.update(dict(
            title=title,
            expense_account=expense_acc,
            enabled=1
        ))
        doc.insert()
        self.add_document(doc)
        self.add_document(frappe.get_doc("Account", doc.expense_account))

        return doc

    def _get_expense_acc(self, title: str) -> str:
        parent = frappe.db.get_value(
            "Account", {
                "account_name": "Indirect Expenses",
                "company": get_default_company(),
            })

        doc = frappe.new_doc("Account")
        doc.update(dict(
            account_name=title,
            company=get_default_company(),
            parent_account=parent,
        ))
        doc.insert()
        return doc.name


class TestExpenseType(unittest.TestCase):
    expense_types: ExpenseTypeFixtures = None

    def setUp(self) -> None:
        self.expense_types = ExpenseTypeFixtures()
        self.expense_types.setUp()

    def tearDown(self):
        self.expense_types.tearDown()

    def test_validate_account_type(self):
        doc = self.expense_types[0]
        doc.expense_account = frappe.db.get_value(
            "Account", {
                "account_name": "Cash",
                "company": get_default_company(),
            }
        )

        with self.assertRaises(Exception):
            doc.validate_account_type()
