# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

# import frappe
import unittest
from typing import List

import frappe

from kallat_erpnext.tests import TestFixture


class UnitSaleEventFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Unit Sale Event"

    def make_fixtures(self):
        pass

    def tearDown(self):
        """
        Order them based on their date_time in decreasing order first
        """
        self.fixtures[self.DEFAULT_DOCTYPE] = sorted(
            list(self.fixtures[self.DEFAULT_DOCTYPE]),
            key=lambda x: x.get("date_time"),
            reverse=True)

        return super().tearDown()

    def load_events(self, unit_sales: List[str]):
        events = frappe.get_all("Unit Sale Event", {"unit_sale": ["IN", unit_sales]})
        for event in events:
            event = frappe.get_doc("Unit Sale Event", event.name)
            self.add_document(event)


class TestUnitSaleEvent(unittest.TestCase):
    pass
