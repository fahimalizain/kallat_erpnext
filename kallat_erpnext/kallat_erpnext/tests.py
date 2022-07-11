from .doctype.kallat_plot.test_kallat_plot import KallatPlotFixtures, TestKallatPlot  # noqa
from .doctype.kallat_project.test_kallat_project import KallatProjectFixtures, TestKallatProject  # noqa
from .doctype.kallat_unit_type.test_kallat_unit_type import KallatUnitTypeFixtures, TestKallatUnitType  # noqa
from .doctype.unit_sale.test_unit_sale import UnitSaleFixtures, TestUnitSale  # noqa
from .doctype.unit_sale_event.test_unit_sale_event import UnitSaleEventFixtures, TestUnitSaleEvent  # noqa

from .test_unit_sale_workflow import get_unit_sale_workflow_tests


def get_kallat_erpnext_module_tests():
    return [
        TestKallatPlot,
        TestKallatProject,
        TestKallatUnitType,
        TestUnitSale,
        TestUnitSaleEvent,
        *get_unit_sale_workflow_tests(),
    ]
