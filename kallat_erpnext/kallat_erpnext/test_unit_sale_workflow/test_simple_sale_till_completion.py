from datetime import datetime
from frappe.utils import get_datetime, add_to_date
from frappe.utils.data import flt, fmt_money

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus, UnitWorkStatus, UnitSale
)
from .utils import TestUnitSaleWorkflowBase


class TestSimpleSaleTillCompletion(TestUnitSaleWorkflowBase):
    def test_simple(self):
        unit_sale = self._get_test_sale()
        _date_time = get_datetime(unit_sale.date_time)

        #################################################
        #               Confirm Booking                 #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._test_confirm_booking(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Sign Agreement                  #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._test_sign_agreement(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Work Progression                #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._test_work_complete_foundation(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._test_work_complete_first_floor_slab(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._test_work_complete_structure(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._test_work_complete_tiling(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Hand Over                       #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._test_hand_over(unit_sale=unit_sale, date_time=_date_time)

        # Hand Over and the last 2% is the final thing
        self.assertEqual(unit_sale.status, UnitSaleStatus.COMPLETED.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.TILING_COMPLETED.value)
        self.assertEqual(unit_sale.balance_due, 0)

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

    def _test_confirm_booking(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_sign_agreement(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_work_complete_foundation(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_work_complete_first_floor_slab(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_work_complete_structure(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_work_complete_tiling(self, unit_sale: UnitSale, date_time: datetime):
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

    def _test_hand_over(self, unit_sale: UnitSale, date_time: datetime):
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
