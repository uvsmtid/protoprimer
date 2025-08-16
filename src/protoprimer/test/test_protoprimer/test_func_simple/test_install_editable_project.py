import subprocess
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfField,
    install_editable_project,
)


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

    # given:

    project_descriptors = [
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project",
            ConfField.field_env_install_extras.value: ["test"],
        },
    ]

    # when:

    install_editable_project(
        "/mock",
        project_descriptors,
    )

    # then:

    expected_command = [
        "/mock/path/to/python",
        "-m",
        "pip",
        "install",
        "--editable",
        "/mock/path/to/project[test]",
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

    # given:

    project_descriptors = [
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project/a",
            ConfField.field_env_install_extras.value: [],
        },
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project/b",
            ConfField.field_env_install_extras.value: [],
        },
        {
            ConfField.field_env_build_root_dir_rel_path.value: "path/to/project/c",
            ConfField.field_env_install_extras.value: ["test"],
        },
    ]

    # when:

    install_editable_project(
        "/mock",
        project_descriptors,
    )

    # then:

    expected_command = [
        "/mock/path/to/python",
        "-m",
        "pip",
        "install",
        "--editable",
        "/mock/path/to/project/a",
        "--editable",
        "/mock/path/to/project/b",
        "--editable",
        "/mock/path/to/project/c[test]",
    ]
    mock_check_call.assert_called_once_with(expected_command)
    mock_get_path_to_curr_python.assert_called_once()
