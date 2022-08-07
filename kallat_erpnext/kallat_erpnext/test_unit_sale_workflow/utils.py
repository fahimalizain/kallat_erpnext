from unittest import TestCase
from datetime import datetime

from frappe.utils import fmt_money, add_to_date, flt

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus, UnitWorkStatus, UnitSale
)
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

    def _get_test_sale(self):
        """
        Gets a single Unit Sale that is fresh and new for testing!
        """
        unit_sale = self.unit_sales.get_simple_submitted_unit_sale()

        self.assertEqual(unit_sale.docstatus, 1)
        self.assertFalse(unit_sale.status)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.NOT_STARTED.value)

        return unit_sale

    def _make_payment_receipt(
            self,
            unit_sale: UnitSale,
            date_time: datetime,
            remarks: str = "Payment",
            amount: float = 0):
        unit_sale.make_payment_receipt(
            amount_received=amount,
            remarks=remarks,
            **{
                "event_datetime": date_time,
            }
        )
        unit_sale.reload()
        print("Payment Made worth", fmt_money(amount), remarks)

    def _confirm_booking(self, unit_sale: UnitSale, date_time: datetime):
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="Booking Fee",
            amount=250000,
        )

        self.assertEqual(unit_sale.total_received, 250000)

        # Confirm Booking after 5minutes
        date_time = add_to_date(date_time, minutes=5)

        unit_sale.confirm_booking(date_time)
        unit_sale.reload()
        self.assertEqual(unit_sale.status, UnitSaleStatus.BOOKED.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.NOT_STARTED.value)

    def _sign_agreement(self, unit_sale: UnitSale, date_time: datetime):
        # To sign the agreement, 40 percent inclusive amount should be paid
        _price = unit_sale.suggested_price
        _total_received = unit_sale.total_received
        _amount_left = flt(_price * 0.4, 2) - _total_received

        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="Agreement 40%",
            amount=_amount_left,
        )
        self.assertTrue(unit_sale.total_received, _amount_left + _total_received)

        # Sign after 5min
        date_time = add_to_date(date_time, minutes=5)
        unit_sale.sign_agreement(
            agreement_price=_price,
            agreement_file=None,
            remarks="Agreement Sign",
            **{
                "event_datetime": date_time,
            })
        unit_sale.reload()
        self.assertEqual(unit_sale.status, UnitSaleStatus.WIP.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.NOT_STARTED.value)

    def _work_complete_foundation(self, unit_sale: UnitSale, date_time: datetime):
        unit_sale.update_work_status(
            new_status=UnitWorkStatus.FOUNDATION_COMPLETED.value,
            **{
                "event_datetime": date_time,
            })

        self.assertEqual(unit_sale.status, UnitSaleStatus.WIP.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.FOUNDATION_COMPLETED.value)

        date_time = add_to_date(date_time, minutes=5)
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            amount=unit_sale.total_due - unit_sale.total_received,
        )

    def _work_complete_first_floor_slab(self, unit_sale: UnitSale, date_time: datetime):
        unit_sale.update_work_status(
            new_status=UnitWorkStatus.FIRST_FLOOR_SLAB_COMPLETED.value,
            **{
                "event_datetime": date_time,
            })

        self.assertEqual(unit_sale.status, UnitSaleStatus.WIP.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.FIRST_FLOOR_SLAB_COMPLETED.value)

        date_time = add_to_date(date_time, minutes=5)
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="First Floor Slab Done",
            amount=unit_sale.total_due - unit_sale.total_received,
        )

    def _work_complete_structure(self, unit_sale: UnitSale, date_time: datetime):
        unit_sale.update_work_status(
            new_status=UnitWorkStatus.STRUCTURE_COMPLETED.value,
            **{
                "event_datetime": date_time,
            })

        self.assertEqual(unit_sale.status, UnitSaleStatus.WIP.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.STRUCTURE_COMPLETED.value)

        date_time = add_to_date(date_time, minutes=5)
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="Structure Done",
            amount=unit_sale.total_due - unit_sale.total_received,
        )

    def _work_complete_tiling(self, unit_sale: UnitSale, date_time: datetime):
        unit_sale.update_work_status(
            new_status=UnitWorkStatus.TILING_COMPLETED.value,
            **{
                "event_datetime": date_time,
            })

        self.assertEqual(unit_sale.status, UnitSaleStatus.WIP.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.TILING_COMPLETED.value)

        date_time = add_to_date(date_time, minutes=5)
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="Tiling Done",
            amount=unit_sale.total_due - unit_sale.total_received,
        )

    def _hand_over(self, unit_sale: UnitSale, date_time: datetime):
        unit_sale.hand_over_unit(remarks="Hand Over!", **{
            "event_datetime": date_time,
        })

        self.assertEqual(unit_sale.status, UnitSaleStatus.HANDED_OVER.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.TILING_COMPLETED.value)

        date_time = add_to_date(date_time, minutes=5)
        self._make_payment_receipt(
            unit_sale=unit_sale,
            date_time=date_time,
            remarks="Hand Over",
            amount=unit_sale.total_due - unit_sale.total_received,
        )

        self.assertEqual(unit_sale.status, UnitSaleStatus.COMPLETED.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.TILING_COMPLETED.value)
        self.assertEqual(unit_sale.balance_due, 0)
