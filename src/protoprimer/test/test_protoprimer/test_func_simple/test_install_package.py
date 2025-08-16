import subprocess
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import install_package


def test_relationship():
    assert_test_module_name_embeds_str(
        install_package.__name__,
    )


@patch(f"{subprocess.__name__}.check_call")
@patch(
    f"{primer_kernel.__name__}.get_path_to_curr_python",
    return_value="/mock/path/to/python",
)
def test_install_package(
    mock_get_path_to_curr_python: MagicMock,
    mock_check_call: MagicMock,
):

    # given:

    package_name = "some_package"

    # when:

    install_package(package_name)

    # then:

    expected_command = [
        "/mock/path/to/python",
        "-m",
        "pip",
        "install",
        package_name,
    ]
    mock_check_call.assert_called_once_with(expected_command)
    mock_get_path_to_curr_python.assert_called_once()
