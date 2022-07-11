# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

import unittest
import random
# import frappe
from kallat_erpnext.tests import TestFixture
from kallat_erpnext.kallat_erpnext.tests import KallatProjectFixtures

from .kallat_unit_type import KallatUnitType


class KallatUnitTypeFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Kallat Unit Type"
        self.dependent_fixtures = [
            KallatProjectFixtures
        ]

    def make_fixtures(self):
        projects = self.get_dependent_fixture_instance("Kallat Project")
        for project in projects:
            for i in range(3):
                d = KallatUnitType(dict(
                    doctype="Kallat Unit Type",
                    title=f"Unit Type #{i + 1}",
                    project=project.name,
                    price=1000000 + 500000 * random.randint(3, 6),
                ))
                d.insert()
                self.add_document(d)


class TestKallatUnitType(unittest.TestCase):
    pass
