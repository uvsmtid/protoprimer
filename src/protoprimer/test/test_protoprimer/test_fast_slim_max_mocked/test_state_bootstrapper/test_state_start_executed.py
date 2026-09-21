import argparse
import os
import sys
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Factory_state_args_parsed,
    Factory_state_proto_kernel_file_abs_path_inited,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_stride_src_updated_reached,
    EnvContext,
    EnvState,
    EnvVar,
    StateStride,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_start_executed.name)


@patch(f"{primer_kernel.__name__}.importlib.import_module")
@patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_src_updated_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_kernel_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_args_parsed.__name__}.create_state_node")
@patch.dict(os.environ, {}, clear=True)
def test_start_executed_imports_and_calls_main_func(
    mock_state_args_parsed,
    mock_state_proto_kernel_file_abs_path_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_stride_src_updated_reached,
    mock_get_stride,
    mock_import_module,
    env_ctx,
):
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_start_executed.name,
    )
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(main_func="my_module:my_func")
    mock_state_proto_kernel_file_abs_path_inited.return_value.eval_own_state.return_value = "/fake/proto_kernel.py"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/cache"
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/venv"
    mock_state_stride_src_updated_reached.return_value.eval_own_state.return_value = StateStride.stride_src_updated
    mock_get_stride.return_value = StateStride.stride_src_updated

    mock_module = MagicMock()
    mock_func = MagicMock()
    mock_module.my_func = mock_func
    mock_import_module.return_value = mock_module

    # when:
    result = env_ctx.eval_state(EnvState.state_start_executed.name)

    # then:
    assert result == 0
    mock_import_module.assert_called_once_with("my_module")
    mock_func.assert_called_once()
    assert os.environ[EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value] == "/fake/proto_kernel.py"
    assert os.environ[EnvVar.var_PROTOPRIMER_MAIN_FUNC.value] == "my_module:my_func"


@patch(f"{primer_kernel.__name__}.importlib.import_module")
@patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_src_updated_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_kernel_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_args_parsed.__name__}.create_state_node")
@patch.dict(os.environ, {}, clear=True)
def test_start_executed_resets_argv_before_calling_main_func(
    mock_state_args_parsed,
    mock_state_proto_kernel_file_abs_path_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_stride_src_updated_reached,
    mock_get_stride,
    mock_import_module,
    env_ctx,
):
    """
    A target function (e.g. a `click` command) parsing `sys.argv` on its own must see a clean
    `argv`, as if started via a dedicated `entry_script`, not the `start`/`main_func` CLI args.
    """
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_start_executed.name,
    )
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(main_func="my_module:my_func")
    mock_state_proto_kernel_file_abs_path_inited.return_value.eval_own_state.return_value = "/fake/proto_kernel.py"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/cache"
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/venv"
    mock_state_stride_src_updated_reached.return_value.eval_own_state.return_value = StateStride.stride_src_updated
    mock_get_stride.return_value = StateStride.stride_src_updated

    mock_module = MagicMock()
    argv_at_call_time = []
    mock_module.my_func = lambda: argv_at_call_time.append(list(sys.argv))
    mock_import_module.return_value = mock_module

    # when:
    with patch.object(sys, "argv", ["/fake/proto_kernel.py", "start", "my_module:my_func"]):
        env_ctx.eval_state(EnvState.state_start_executed.name)

    # then:
    assert argv_at_call_time == [["/fake/proto_kernel.py"]]


@patch(f"{primer_kernel.__name__}.importlib.import_module")
@patch(f"{primer_kernel.__name__}.{EnvContext.__name__}.{EnvContext.get_stride.__name__}")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_stride_src_updated_reached.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_proto_kernel_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Factory_state_args_parsed.__name__}.create_state_node")
@patch.dict(os.environ, {}, clear=True)
def test_start_executed_rejects_malformed_main_func(
    mock_state_args_parsed,
    mock_state_proto_kernel_file_abs_path_inited,
    mock_state_local_cache_dir_abs_path_inited,
    mock_state_local_venv_dir_abs_path_inited,
    mock_state_stride_src_updated_reached,
    mock_get_stride,
    mock_import_module,
    env_ctx,
):
    """
    A `main_func` without the `module_name:function_name` separator must be rejected
    before anything is imported (uncaught, per `parse_main_func`).
    """
    # given:
    assert_parent_factories_mocked(
        env_ctx,
        EnvState.state_start_executed.name,
    )
    mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(main_func="invalid_format")
    mock_state_proto_kernel_file_abs_path_inited.return_value.eval_own_state.return_value = "/fake/proto_kernel.py"
    mock_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/cache"
    mock_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/fake/venv"
    mock_state_stride_src_updated_reached.return_value.eval_own_state.return_value = StateStride.stride_src_updated
    mock_get_stride.return_value = StateStride.stride_src_updated

    # when/then:
    with pytest.raises(ValueError):
        env_ctx.eval_state(EnvState.state_start_executed.name)

    mock_import_module.assert_not_called()
