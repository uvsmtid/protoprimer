from unittest.mock import (
    patch,
    call,
)
import logging
import pytest
import subprocess

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    search_python_file_abs_path_by_basename,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        search_python_file_abs_path_by_basename.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.shutil.which")
def test_finds_python_on_first_try(
    mock_shutil_which,
    mock_get_python_version,
):
    """
    Tests that `search_python_file_abs_path_by_basename` finds a `python` executable and returns its path.
    """

    # given:

    required_version = (3, 9, 1)
    expected_path = "/usr/bin/python3.9.1"
    mock_shutil_which.return_value = expected_path
    mock_get_python_version.return_value = (3, 9, 1)

    # when:

    result_path = search_python_file_abs_path_by_basename(required_version)

    # then:

    assert result_path == expected_path
    mock_shutil_which.assert_called_once_with("python3.9.1")
    mock_get_python_version.assert_called_once_with(expected_path)


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.shutil.which")
def test_finds_python_on_fallback(
    mock_shutil_which,
    mock_get_python_version,
):
    """
    Tests that `search_python_file_abs_path_by_basename` tries multiple basenames.
    """

    # given:

    required_version = (3, 9, 1)
    expected_path = "/usr/bin/python3.9"
    mock_shutil_which.side_effect = [None, expected_path]
    # a different patch version:
    mock_get_python_version.return_value = (3, 9, 5)

    # when:

    result_path = search_python_file_abs_path_by_basename(required_version)

    # then:

    assert result_path == expected_path
    assert mock_shutil_which.call_count == 2
    mock_shutil_which.assert_has_calls(
        [
            call("python3.9.1"),
            call("python3.9"),
        ]
    )
    mock_get_python_version.assert_called_once_with(expected_path)


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.shutil.which")
def test_handles_verification_failure(
    mock_shutil_which,
    mock_get_python_version,
    caplog,
):
    """
    Tests that `search_python_file_abs_path_by_basename` continues if version check fails and succeeds eventually.
    """

    # given:

    required_version = (3, 9, 0)
    failing_path = "/usr/bin/corrupt_python"
    working_path = "/usr/bin/python3"
    mock_shutil_which.side_effect = [failing_path, working_path]
    mock_get_python_version.side_effect = [FileNotFoundError, (3, 9, 2)]

    # when:

    with caplog.at_level(logging.WARNING):
        result_path = search_python_file_abs_path_by_basename(required_version)

    # then:

    assert result_path == working_path
    assert mock_shutil_which.call_count == 2
    assert "failed without returning its version" in caplog.text
    assert mock_get_python_version.call_count == 2
    mock_get_python_version.assert_has_calls(
        [
            call(failing_path),
            call(working_path),
        ]
    )


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.shutil.which")
def test_returns_none_if_no_python_found(
    mock_shutil_which,
    mock_get_python_version,
):
    """
    Tests that `search_python_file_abs_path_by_basename` returns `None` if no executable is found.
    """

    # given:

    required_version = (3, 10, 0)
    mock_shutil_which.return_value = None

    # when:

    result_path = search_python_file_abs_path_by_basename(required_version)

    # then:

    assert result_path is None
    # All basenames tried:
    assert mock_shutil_which.call_count == 4
    mock_get_python_version.assert_not_called()


@patch(f"{protoprimer.primer_kernel.__name__}.get_python_version")
@patch(f"{protoprimer.primer_kernel.__name__}.shutil.which")
def test_returns_none_if_all_verifications_fail(
    mock_shutil_which,
    mock_get_python_version,
    caplog,
):
    """
    Tests that `search_python_file_abs_path_by_basename` returns `None` if all found executables fail verification.
    """

    # given:

    required_version = (3, 11, 0)
    path1 = "/path/to/python3.11"
    path2 = "/path/to/python3"
    mock_shutil_which.side_effect = [path1, path2, None, None]
    mock_get_python_version.side_effect = [
        subprocess.CalledProcessError(1, "cmd"),
        FileNotFoundError,
    ]

    # when:

    with caplog.at_level(logging.WARNING):
        result_path = search_python_file_abs_path_by_basename(required_version)

    # then:

    assert result_path is None
    assert mock_shutil_which.call_count == 4
    assert mock_get_python_version.call_count == 2
    assert caplog.text.count("failed without returning its version") == 2
