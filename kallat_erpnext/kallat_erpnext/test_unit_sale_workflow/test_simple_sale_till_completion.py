from frappe.utils import get_datetime, add_to_date

from .utils import TestUnitSaleWorkflowBase


class TestSimpleSaleTillCompletion(TestUnitSaleWorkflowBase):
    def test_simple(self):
        unit_sale = self.unit_sales.get_simple_submitted_unit_sale()
        _date_time = get_datetime(unit_sale.date_time)

        #################################################
        #               Confirm Booking                 #
        #################################################
        _date_time = add_to_date(_date_time, days=1)
        unit_sale.make_payment_receipt(
            amount_received=250000,
            remarks="Booking Fee",
            **{
                "event_datetime": _date_time,
            }
        )
        unit_sale.reload()

        self.assertEqual(unit_sale.total_received, 250000)
