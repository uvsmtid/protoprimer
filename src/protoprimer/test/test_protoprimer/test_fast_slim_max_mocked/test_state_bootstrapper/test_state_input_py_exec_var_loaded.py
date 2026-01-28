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
    StateStride,
)


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_input_py_exec_var_loaded.name)


@patch.dict(os.environ, {EnvVar.var_PROTOPRIMER_PY_EXEC.value: "stride_py_arbitrary"})
def test_stride_py_arbitrary():
    # given:
    mock_env_ctx = MagicMock()
    mock_env_ctx.set_max_stride.side_effect = lambda x: x

    # when:
    result = Bootstrapper_state_input_py_exec_var_loaded(
        mock_env_ctx
    )._eval_state_once()

    # then:
    assert result == StateStride.stride_py_arbitrary


@patch.dict(os.environ, {}, clear=True)
def test_py_exec_stride_py_unknown():
    # given:
    mock_env_ctx = MagicMock()
    mock_env_ctx.set_max_stride.side_effect = lambda x: x

    # when:
    result = Bootstrapper_state_input_py_exec_var_loaded(
        mock_env_ctx
    )._eval_state_once()

    # then:
    assert result == StateStride.stride_py_unknown
