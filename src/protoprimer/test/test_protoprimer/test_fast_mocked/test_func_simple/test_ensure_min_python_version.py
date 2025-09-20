from unittest.mock import patch

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ensure_min_python_version,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ensure_min_python_version.__name__,
    )


class ThisTestClass(BaseTestClass):

    @patch("sys.version_info", (3, 8, 0))
    def test_version_succeeds(self):
        # FT_84_11_73_28: supported python versions:
        ensure_min_python_version()

    @patch("sys.version_info", (3, 7, 5))
    def test_version_fails(self):
        # FT_84_11_73_28: supported python versions:
        with self.assertRaises(AssertionError) as context:
            ensure_min_python_version()
        self.assertIn("below the min required", str(context.exception))
