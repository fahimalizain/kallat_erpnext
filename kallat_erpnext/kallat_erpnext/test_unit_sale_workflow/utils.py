from unittest import TestCase

from kallat_erpnext.test_customer import CustomerFixtures
from kallat_erpnext.kallat_erpnext.tests import (
    KallatPlotFixtures,
    KallatProjectFixtures,
    KallatUnitTypeFixtures,
    UnitSaleFixtures,
    UnitSaleEventFixtures)


class TestUnitSaleWorkflowBase(TestCase):
    customers: CustomerFixtures = None
    projects: KallatProjectFixtures = None
    plots: KallatPlotFixtures = None
    unit_types: KallatUnitTypeFixtures = None
    unit_sales: UnitSaleFixtures = None
    unit_sale_events: UnitSaleEventFixtures = None

    @classmethod
    def setUpClass(cls):
        cls.customers = CustomerFixtures()
        cls.projects = KallatProjectFixtures()
        cls.plots = KallatPlotFixtures()
        cls.unit_types = KallatUnitTypeFixtures()
        cls.unit_sales = UnitSaleFixtures()
        cls.unit_sale_events = UnitSaleEventFixtures()

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
        self.unit_sale_events.setUp()

    def tearDown(self):
        self.unit_sale_events.load_events([x.name for x in self.unit_sales])
        self.unit_sale_events.tearDown()

        self.unit_sales.tearDown()
