import os
from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    Bootstrapper_state_input_py_exec_var_loaded,
    EnvState,
    EnvVar,
    PythonExecutable,
)


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_input_py_exec_var_loaded.name)


@patch.dict(os.environ, {EnvVar.var_PROTOPRIMER_PY_EXEC.value: "py_exec_arbitrary"})
def test_py_exec_arbitrary():
    # given:
    mock_env_ctx = MagicMock()

    # when:
    result = Bootstrapper_state_input_py_exec_var_loaded(
        mock_env_ctx
    )._eval_state_once()

    # then:
    assert result == PythonExecutable.py_exec_arbitrary


@patch.dict(os.environ, {}, clear=True)
def test_py_exec_unknown():
    # given:
    mock_env_ctx = MagicMock()

    # when:
    result = Bootstrapper_state_input_py_exec_var_loaded(
        mock_env_ctx
    )._eval_state_once()

    # then:
    assert result == PythonExecutable.py_exec_unknown
