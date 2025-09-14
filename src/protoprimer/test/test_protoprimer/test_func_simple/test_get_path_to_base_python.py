import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import get_path_to_base_python


def test_relationship():
    assert_test_module_name_embeds_str(
        get_path_to_base_python.__name__,
    )


@patch(f"sys.base_prefix", "/mock/base/prefix")
def test_get_path_to_base_python():

    # when:

    actual_path = get_path_to_base_python()

    # then:

    expected_path = os.path.join(
        "/mock/base/prefix",
        "bin",
        "python",
    )
    assert actual_path == expected_path
