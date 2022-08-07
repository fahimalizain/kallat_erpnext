
from .utils import TestUnitSaleWorkflowBase


class TestEventCancellation(TestUnitSaleWorkflowBase):
    """
    Cancellation should fail when there are events that exists post the date of Event being deleted
    """

    def test_simple(self):
        pass
