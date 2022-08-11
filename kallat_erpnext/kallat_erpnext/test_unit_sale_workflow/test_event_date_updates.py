from frappe.utils import add_to_date, get_datetime
from .utils import TestUnitSaleWorkflowBase


class TestEventDateUpdates(TestUnitSaleWorkflowBase):
    """
    Date Updates should fail when there are events that exists post the date of Event being updated
    """

    def test_simple(self):
        unit_sale = self._get_test_sale_structure_completed()
        events = self.unit_sales.get_all_events_of(unit_sale)

        with self.assertRaises(Exception) as exc:
            event = events[-2]
            event.date_time = add_to_date(
                get_datetime(events[-1].date_time),
                hours=-1
            )
            event.save()

        self.assertIn("You cannot make updates to this event when", str(exc.exception))
