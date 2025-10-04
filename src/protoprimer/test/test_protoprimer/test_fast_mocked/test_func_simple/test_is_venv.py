from unittest.mock import patch

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import is_venv


def test_relationship():
    assert_test_module_name_embeds_str(
        is_venv.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.sys")
def test_is_venv_when_in_venv(
    mock_sys,
):
    # given:
    mock_sys.prefix = "/path/to/venv"
    mock_sys.base_prefix = "/path/to/python"

    # when:
    result = is_venv()

    # then:
    assert result is True


@patch(f"{protoprimer.primer_kernel.__name__}.sys")
def test_is_venv_when_not_in_venv(
    mock_sys,
):
    # given:
    mock_sys.prefix = "/path/to/python"
    mock_sys.base_prefix = "/path/to/python"

    # when:
    result = is_venv()

    # then:
    assert result is False
