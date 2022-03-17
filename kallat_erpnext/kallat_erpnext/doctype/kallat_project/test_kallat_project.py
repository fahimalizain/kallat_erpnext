# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

import frappe
import unittest

from faker import Faker
from kallat_erpnext.tests import TestFixture


class KallatProjectFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Kallat Project"

    def make_fixtures(self):
        f = Faker()
        projects = ["Pearl-X", "Diamond-A"]

        for p in projects:
            self.add_document(frappe.get_doc(dict(
                doctype="Kallat Project",
                title=p,
                address=f.address(),
            )).insert())


class TestKallatProject(unittest.TestCase):
    pass
