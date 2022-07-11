# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

import unittest
import random

import frappe

from kallat_erpnext.kallat_erpnext.doctype.kallat_project.test_kallat_project import \
    KallatProjectFixtures
from kallat_erpnext.tests import TestFixture


class KallatPlotFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Kallat Plot"
        self.dependent_fixtures = [KallatProjectFixtures]

    def make_fixtures(self):
        from faker import Faker
        f = Faker()

        for project in self.get_dependencies("Kallat Project"):
            for i in range(5):
                self.add_document(frappe.get_doc(
                    doctype="Kallat Plot",
                    title=f"{project.name[:3].upper()}-{f.random_int()}{i}",
                    project=project.name,
                    price=2000000 + 500000 * random.randint(3, 6),
                ).insert())


class TestKallatPlot(unittest.TestCase):
    pass
