from unittest.mock import (
    MagicMock,
    patch,
)
import logging
import pytest

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    select_python_file_abs_path,
    SelectorFunc,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        select_python_file_abs_path.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.import_proto_module")
def test_select_python_finds_executable_which_returns_its_version(
    mock_import_proto_module,
    mock_get_python_version,
):
    """
    Tests that `select_python_file_abs_path` successfully finds a `python` executable that returns its version.
    """

    # given:

    mock_selector_module = MagicMock()
    mock_import_proto_module.return_value = mock_selector_module
    mock_external_selector_func = getattr(mock_selector_module, SelectorFunc.select_python_file_abs_path.value)
    expected_path = "/path/to/python3.8"
    mock_external_selector_func.return_value = expected_path

    # Mock the verification call that happens after the external script returns.
    mock_get_python_version.return_value = (3, 8, 5)

    selector_script_path = "/path/to/selector.py"
    required_version = (3, 8, 0)

    # when:

    result_path = select_python_file_abs_path(required_version, selector_script_path)

    # then:

    assert result_path == expected_path
    mock_import_proto_module.assert_called_once_with("python_selector_module", selector_script_path)
    mock_external_selector_func.assert_called_once_with(required_version)
    mock_get_python_version.assert_called_once_with(expected_path)


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.import_proto_module")
def test_select_python_cannot_find_executable_which_returns_its_version(
    mock_import_proto_module,
    mock_get_python_version,
    caplog,
):
    """
    Tests that `select_python_file_abs_path` returns `None`
    if the `python` executable verification raises an exception.
    """

    # given:

    mock_selector_module = MagicMock()
    mock_import_proto_module.return_value = mock_selector_module
    mock_external_selector_func = getattr(mock_selector_module, SelectorFunc.select_python_file_abs_path.value)
    selected_path = "/path/to/nonexistent_python"
    mock_external_selector_func.return_value = selected_path

    # The verification step fails by raising `FileNotFoundError`.
    mock_get_python_version.side_effect = FileNotFoundError("python not found")

    selector_script_path = "/path/to/selector.py"
    required_version = (3, 8, 0)

    # when:

    result_path = select_python_file_abs_path(required_version, selector_script_path)

    # then:

    # The function should catch the exception and return `None`.
    assert result_path is None

    # A warning should be logged about the verification failure.
    assert "failed without returning its version" in caplog.text

    # Verify mocks were called correctly:
    mock_import_proto_module.assert_called_once_with("python_selector_module", selector_script_path)
    mock_external_selector_func.assert_called_once_with(required_version)
    mock_get_python_version.assert_called_once_with(selected_path)


@patch(f"{protoprimer.primer_kernel.__name__}.import_proto_module")
def test_select_python_finds_no_matching_version(mock_import_proto_module):
    """
    Tests that `select_python_file_abs_path` returns `None` when the delegated selector returns `None`.
    """

    # given:

    mock_selector_module = MagicMock()
    mock_import_proto_module.return_value = mock_selector_module
    mock_external_selector_func = getattr(
        mock_selector_module,
        SelectorFunc.select_python_file_abs_path.value,
    )
    mock_external_selector_func.return_value = None

    selector_script_path = "/path/to/selector.py"
    required_version = (3, 8, 0)

    # when:

    result_path = select_python_file_abs_path(required_version, selector_script_path)

    # then:

    assert result_path is None

    mock_import_proto_module.assert_called_once_with("python_selector_module", selector_script_path)

    mock_external_selector_func.assert_called_once_with(required_version)
