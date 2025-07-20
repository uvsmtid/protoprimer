import subprocess
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import install_editable_project


def test_relationship():
    assert_test_module_name_embeds_str(
        install_editable_project.__name__,
    )


@patch(f"{subprocess.__name__}.check_call")
@patch(
    f"{primer_kernel.__name__}.get_path_to_curr_python",
    return_value="/mock/path/to/python",
)
def test_install_editable_single_project(
    mock_get_path_to_curr_python: MagicMock,
    mock_check_call: MagicMock,
):
    """
    Test install_editable_project when no extras are provided.
    """
    project_abs_path_list = [
        "path/to/project",
    ]

    install_editable_project(project_abs_path_list)

    expected_command = [
        "/mock/path/to/python",
        "-m",
        "pip",
        "install",
        "--editable",
        "path/to/project",
    ]
    mock_check_call.assert_called_once_with(expected_command)
    mock_get_path_to_curr_python.assert_called_once()


@patch(f"{subprocess.__name__}.check_call")
@patch(
    f"{primer_kernel.__name__}.get_path_to_curr_python",
    return_value="/mock/path/to/python",
)
def test_install_editable_multiple_projects(
    mock_get_path_to_curr_python: MagicMock,
    mock_check_call: MagicMock,
):
    """
    Test install_editable_project when no extras are provided.
    """
    project_rel_path_list = [
        "path/to/project/a",
        "path/to/project/b",
        "path/to/project/c",
    ]

    install_editable_project(project_rel_path_list)

    expected_command = [
        "/mock/path/to/python",
        "-m",
        "pip",
        "install",
        "--editable",
        "path/to/project/a",
        "--editable",
        "path/to/project/b",
        "--editable",
        "path/to/project/c",
    ]
    mock_check_call.assert_called_once_with(expected_command)
    mock_get_path_to_curr_python.assert_called_once()
