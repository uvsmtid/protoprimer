import importlib
import os
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstInput,
    EnvVar,
    PythonExecutable,
    run_main,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        run_main.__name__,
    )


@patch(f"{importlib.__name__}.import_module")
def test_run_main_neo_runtime(mock_import_module):
    # given:
    mock_neo_main = MagicMock()
    mock_import_module.return_value = MagicMock(neo_main_function=mock_neo_main)

    # when:
    run_main(
        "neo_main_module",
        "neo_main_function",
    )

    # then:
    mock_import_module.assert_called_once_with("neo_main_module")
    mock_neo_main.assert_called_once()


@patch(f"{importlib.__name__}.import_module")
@patch(f"{protoprimer.primer_kernel.__name__}.main")
def test_run_main_proto_runtime(mock_main, mock_import_module):
    # given:
    mock_import_module.side_effect = ImportError

    # when:
    run_main(
        "neo_main_module",
        "neo_main_function",
    )

    # then:
    mock_import_module.assert_called_once_with("neo_main_module")
    mock_main.assert_called_once()


@patch(f"{importlib.__name__}.import_module")
@patch(f"{os.__name__}.getenv")
def test_run_main_raises_assertion_error(mock_getenv, mock_import_module):
    # given:
    mock_import_module.side_effect = ImportError
    mock_getenv.return_value = PythonExecutable.py_exec_updated_client_package.name

    # when/then:
    with pytest.raises(AssertionError):
        run_main(
            "neo_main_module",
            "neo_main_function",
        )
    mock_getenv.assert_called_once_with(
        EnvVar.var_PROTOPRIMER_PY_EXEC.value,
        ConfConstInput.default_PROTOPRIMER_PY_EXEC,
    )
