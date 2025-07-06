from inspect import currentframe
from unittest import TestCase

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase


class BaseTestClass(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None


class BasePyfakefsTestClass(PyfakefsTestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None


def assert_test_module_name_embeds_str(
    prod_name: str,
):
    """
    Ensure caller test module name contains given `prod_name`.
    """
    caller_frame = currentframe().f_back
    simple_test_module_name = caller_frame.f_globals["__name__"].split(".")[-1]
    _assert_test_name_embeds_prod_name(prod_name, simple_test_module_name)


def assert_test_func_name_embeds_str(
    prod_name: str,
):
    """
    Ensure caller test function name contains given `prod_name`.
    """
    caller_func_name = currentframe().f_back.f_code.co_name
    _assert_test_name_embeds_prod_name(prod_name, caller_func_name)


def _assert_test_name_embeds_prod_name(
    prod_name: str,
    test_name: str,
):
    """
    This function ensures that names in prod code and test code do not diverge due to refactoring.

    That programmatically establishes relationship between prod code and test code via cross-references.
    This function should not be called directly (with its `str` args) -
    that defeat the purpose as strings easily diverge.
    Instead, an appropriate wrapper function should be called with references (e.g., to classes).
    """
    assert prod_name in test_name
