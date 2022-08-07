from frappe.utils import get_datetime, add_to_date

from kallat_erpnext.kallat_erpnext import (
    UnitSaleStatus, UnitWorkStatus
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
        self._confirm_booking(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Sign Agreement                  #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._sign_agreement(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Work Progression                #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._work_complete_foundation(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._work_complete_first_floor_slab(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._work_complete_structure(unit_sale=unit_sale, date_time=_date_time)

        _date_time = add_to_date(_date_time, days=1)
        self._work_complete_tiling(unit_sale=unit_sale, date_time=_date_time)

        #################################################
        #               Hand Over                       #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        self._hand_over(unit_sale=unit_sale, date_time=_date_time)

        # Hand Over and the last 2% is the final thing
        self.assertEqual(unit_sale.status, UnitSaleStatus.COMPLETED.value)
        self.assertEqual(unit_sale.work_status, UnitWorkStatus.TILING_COMPLETED.value)
        self.assertEqual(unit_sale.balance_due, 0)
