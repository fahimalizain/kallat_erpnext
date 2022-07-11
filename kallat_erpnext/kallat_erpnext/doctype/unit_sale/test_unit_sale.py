# Copyright (c) 2022, Fahim Ali Zain and Contributors
# See license.txt

import unittest
import random

import frappe
from frappe.utils import flt

from kallat_erpnext.tests import TestFixture
from kallat_erpnext.test_customer import CustomerFixtures
from kallat_erpnext.kallat_erpnext.tests import (
    KallatPlotFixtures, KallatProjectFixtures, KallatUnitTypeFixtures)

from .unit_sale import UnitSale


class UnitSaleFixtures(TestFixture):
    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Unit Sale"
        self.dependent_fixtures = [
            CustomerFixtures,
            KallatProjectFixtures,
            KallatPlotFixtures,
            KallatUnitTypeFixtures,
        ]

    def make_fixtures(self):
        pass

    def get_simple_unit_sale(self) -> UnitSale:
        unit_sale = frappe.new_doc("Unit Sale")
        project = random.choice(self.get_dependencies("Kallat Project"))
        unit_type = random.choice(frappe.get_all("Kallat Unit Type", {"project": project.name}))
        plot = random.choice(frappe.get_all(
            "Kallat Plot", {"project": project.name, "occupied": 0}))
        customer = random.choice(self.get_dependencies("Customer"))

        unit_sale.update(dict(
            customer=customer.name,
            project=project.name,
            unit_type=unit_type.name,
            plot=plot.name,
            date_time="2020-01-01 10:00:00",
        ))

        return unit_sale

    def get_simple_submitted_unit_sale(self):
        unit_sale = self.get_simple_unit_sale()
        unit_sale.docstatus = 1
        unit_sale.save()
        unit_sale.reload()

        self.add_document(unit_sale)
        return unit_sale


class TestUnitSale(unittest.TestCase):
    customers: CustomerFixtures = None
    projects: KallatProjectFixtures = None
    plots: KallatPlotFixtures = None
    unit_types: KallatUnitTypeFixtures = None
    unit_sales: UnitSaleFixtures = None

    @classmethod
    def setUpClass(cls):
        cls.customers = CustomerFixtures()
        cls.projects = KallatProjectFixtures()
        cls.plots = KallatPlotFixtures()
        cls.unit_types = KallatUnitTypeFixtures()
        cls.unit_sales = UnitSaleFixtures()

        cls.customers.setUp()
        cls.projects.setUp()
        cls.plots.setUp()
        cls.unit_types.setUp()

    @classmethod
    def tearDownClass(cls):
        cls.unit_types.tearDown()
        cls.plots.tearDown()
        cls.projects.tearDown()
        cls.customers.tearDown()

    def setUp(self):
        self.unit_sales.setUp()

    def tearDown(self):
        self.unit_sales.tearDown()

    def test_validate_plot(self):
        """
        - Get Simple Unit Sale
        - Assert that the Project is valid
        - Set Plot that belongs to different Project
        - Assert Invalid
        """
        unit_sale = self.unit_sales.get_simple_unit_sale()

        self.assertEqual(
            unit_sale.project,
            frappe.db.get_value("Kallat Plot", unit_sale.plot, "project"))
        unit_sale.validate_plot()

        # Set invalid plot
        invalid_plot = random.choice(frappe.get_all(
            "Kallat Plot",
            {"project": ["!=", unit_sale.project], "occupied": 0},
            ["name", "title"]))
        unit_sale.plot = invalid_plot.name

        with self.assertRaises(Exception) as _exc:
            unit_sale.validate_plot()

        self.assertEqual(
            f"Plot {invalid_plot.title} do not belong to project {unit_sale.project}",
            str(_exc.exception)
        )

    def test_validate_unit_type(self):
        """
        - Get Simple Unit Sale
        - Assert that Project is valid on unit type
        - Set UnitType with different Project
        - Assert Invalid
        """
        unit_sale = self.unit_sales.get_simple_unit_sale()

        self.assertEqual(
            unit_sale.project,
            frappe.db.get_value("Kallat Unit Type", unit_sale.unit_type, "project"))
        unit_sale.validate_unit_type()

        # Set invalid unit type
        invalid_unit_type = random.choice(frappe.get_all(
            "Kallat Unit Type",
            {"project": ["!=", unit_sale.project]},
            ["name", "title"]))
        unit_sale.unit_type = invalid_unit_type.name

        with self.assertRaises(Exception) as _exc:
            unit_sale.validate_unit_type()

        self.assertEqual(
            f"UnitType {invalid_unit_type.title} do not belong to project {unit_sale.project}",
            str(_exc.exception)
        )

    def test_suggested_price(self):
        """
        Suggested Price = Plot.price + UnitType.price
        """
        unit_sale = self.unit_sales.get_simple_unit_sale()
        unit_sale.calculate_suggested_price()

        plot_price = frappe.db.get_value("Kallat Plot", unit_sale.plot, "price")
        unit_type_price = frappe.db.get_value("Kallat Unit Type", unit_sale.unit_type, "price")
        self.assertEqual(
            unit_sale.suggested_price,
            flt(plot_price + unit_type_price, 2)
        )

        # When suggested_price is set manually, it will not be overridden
        unit_sale.suggested_price = 100000
        unit_sale.calculate_suggested_price()
        self.assertEqual(unit_sale.suggested_price, 100000)
