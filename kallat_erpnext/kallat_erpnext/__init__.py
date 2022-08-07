from unittest import TestLoader, TestSuite
from .enums import (  # noqa: F401
    KallatPlotStatus,
    UnitSaleStatus,
    UnitWorkStatus,
    UnitSaleEventType,
)

from .doctype.kallat_project.kallat_project import KallatProject  # noqa: F401
from .doctype.kallat_plot.kallat_plot import KallatPlot  # noqa: F401
from .doctype.unit_sale_event.unit_sale_event import UnitSaleEvent  # noqa: F401
from .doctype.unit_sale.unit_sale import UnitSale  # noqa: F401


def load_tests(loader: TestLoader, test_classes, pattern):
    suite = TestSuite()
    _test_classes = []

    from .tests import get_kallat_erpnext_module_tests
    _test_classes.extend(get_kallat_erpnext_module_tests())

    for test_class in _test_classes:
        t = loader.loadTestsFromTestCase(test_class)
        suite.addTests(t)

    return suite
