from __future__ import annotations

import subprocess
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import get_python_version


def test_relationship():
    assert_test_module_name_embeds_str(
        get_python_version.__name__,
    )


@patch(f"{subprocess.__name__}.{subprocess.check_output.__name__}")
def test_get_python_version(mock_check_output):

    # given:

    path_to_python = "/some/python/path"
    # The output contains a newline that gets stripped.
    mock_check_output.return_value = "(3, 9, 5)\n"

    expected_version_tuple = (3, 9, 5)

    # when:
    python_version: tuple[int, int, int] = get_python_version(
        path_to_python=path_to_python
    )

    # then:
    assert python_version == expected_version_tuple
    mock_check_output.assert_called_once()
