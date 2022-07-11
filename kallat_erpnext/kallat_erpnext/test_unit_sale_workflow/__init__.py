from unittest import TestLoader, TestSuite


def load_tests(loader: TestLoader, test_classes, pattern):
    suite = TestSuite()
    _test_classes = []

    _test_classes.extend(get_unit_sale_workflow_tests())

    for test_class in _test_classes:
        t = loader.loadTestsFromTestCase(test_class)
        suite.addTests(t)

    return suite


def get_unit_sale_workflow_tests():
    return []
