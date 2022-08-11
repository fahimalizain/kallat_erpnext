
from .utils import TestUnitSaleWorkflowBase


class TestEventCancellation(TestUnitSaleWorkflowBase):
    """
    Cancellation should fail when there are events that exists post the date of Event being deleted
    """

    def test_simple(self):
        unit_sale = self._get_test_sale_structure_completed()
        events = self.unit_sales.get_all_events_of(unit_sale)

        with self.assertRaises(Exception) as exc:
            events[-2].cancel()

        self.assertIn("You cannot cancel this event when", str(exc.exception))
