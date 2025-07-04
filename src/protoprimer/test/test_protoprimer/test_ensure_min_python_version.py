from unittest.mock import patch

from protoprimer.primer_kernel import (
    ensure_min_python_version,
)
from local_test import BaseTestClass


class ThisTestClass(BaseTestClass):

    @patch("sys.version_info", (3, 8, 0))
    def test_version_succeeds(self):
        # FS_84_11_73_28: supported python versions:
        ensure_min_python_version()

    @patch("sys.version_info", (3, 7, 5))
    def test_version_fails(self):
        # FS_84_11_73_28: supported python versions:
        with self.assertRaises(AssertionError) as context:
            ensure_min_python_version()
        self.assertIn("below the min required", str(context.exception))
