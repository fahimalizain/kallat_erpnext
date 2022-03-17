# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

# import frappe
import unittest
from kallat_erpnext.tests import TestFixture


class UnitSaleFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Unit Sale"


class TestUnitSale(unittest.TestCase):
    pass
