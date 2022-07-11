from enum import Enum
from unittest import TestLoader, TestSuite


class KallatPlotStatus(Enum):
    EMPTY_PLOT = "Empty Plot"
    BOOKED = "Booked"
    WIP = "Work In Progress"
    COMPLETED = "Completed"


class UnitSaleStatus(Enum):
    NONE = ""
    BOOKED = "Booked"
    AGREEMENT_SIGNED = "Agreement Signed"
    WIP = "Work In Progress"
    HANDED_OVER = "Handed Over"
    COMPLETED = "Completed"


class UnitWorkStatus(Enum):
    NOT_STARTED = "Not Started"
    FOUNDATION_COMPLETED = "Foundation Completed"
    FIRST_FLOOR_SLAB_COMPLETED = "1st Floor Slab Completed"
    STRUCTURE_COMPLETED = "Structure Completed"
    TILING_COMPLETED = "Tiling Completed"


class UnitSaleEventType(Enum):
    UNIT_SALE_UPDATE = "Unit Sale Update"
    WORK_STATUS_UPDATE = "Work Status Update"
    PAYMENT_RECEIPT = "Payment Receipt"
    LATE_FEE_APPLIED = "Late Fee Applied"
    ADD_EXTRA_WORK = "Add Extra Work"


def load_tests(loader: TestLoader, test_classes, pattern):
    suite = TestSuite()
    _test_classes = []

    from .tests import get_kallat_erpnext_module_tests
    _test_classes.extend(get_kallat_erpnext_module_tests())

    for test_class in _test_classes:
        t = loader.loadTestsFromTestCase(test_class)
        suite.addTests(t)

    return suite
