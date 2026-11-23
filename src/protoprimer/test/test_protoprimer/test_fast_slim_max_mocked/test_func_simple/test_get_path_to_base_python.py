import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _ConfConstGeneral,
    _get_path_to_base_python,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _get_path_to_base_python.__name__,
    )


@patch(f"sys.base_prefix", "/mock/base/prefix")
def test_get_path_to_base_python():

    # when:

    actual_path = _get_path_to_base_python()

    # then:

    expected_path = os.path.join(
        "/mock/base/prefix",
        _ConfConstGeneral.file_rel_path_base_python_bin,
        _ConfConstGeneral.name_python_executable,
    )
    assert actual_path == expected_path
