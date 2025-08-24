import argparse
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_py_exec_arg_loaded,
    Bootstrapper_state_input_wizard_stage_arg_loaded,
    CommandArg,
    EnvContext,
    EnvState,
    PythonExecutable,
    WizardStage,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
    )


@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.get_path_to_base_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(f"{primer_kernel.__name__}.is_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
)
def test_py_exec_unknown_in_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_arg_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    mock_is_venv,
    mock_switch_python,
    mock_get_path_to_base_python,
    mock_get_path_to_curr_python,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            CommandArg.name_py_exec.value: PythonExecutable.py_exec_unknown.name,
            CommandArg.name_wizard_stage.value: WizardStage.wizard_started.name,
        },
    )
    mock_state_input_py_exec_arg_loaded.return_value = PythonExecutable.py_exec_unknown
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    mock_is_venv.return_value = True

    mock_get_path_to_curr_python.return_value = "/path/to/venv/bin/python"
    mock_get_path_to_base_python.return_value = "/usr/bin/python"

    # when:

    env_ctx.state_graph.eval_state(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
    )

    # then:

    mock_switch_python.assert_called_once_with(
        curr_py_exec=PythonExecutable.py_exec_unknown,
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=PythonExecutable.py_exec_arbitrary,
        next_python_path=mock_get_path_to_base_python.return_value,
        proto_code_abs_file_path=None,
        wizard_stage=WizardStage.wizard_started,
    )


@patch(f"{primer_kernel.__name__}.is_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
)
def test_py_exec_unknown_not_in_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_arg_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    mock_is_venv,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            CommandArg.name_py_exec.value: PythonExecutable.py_exec_unknown.name,
        },
    )
    mock_state_input_py_exec_arg_loaded.return_value = PythonExecutable.py_exec_unknown
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    mock_is_venv.return_value = False

    # when:

    ret_val: str = env_ctx.state_graph.eval_state(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
    )

    # then:

    assert ret_val == primer_kernel.__file__


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
)
def test_py_exec_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_arg_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
    )

    proto_code_abs_file_path = "/path/to/proto_kernel.py"

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            CommandArg.name_py_exec.value: PythonExecutable.py_exec_venv.name,
            CommandArg.name_proto_code.value: proto_code_abs_file_path,
        },
    )
    mock_state_input_py_exec_arg_loaded.return_value = PythonExecutable.py_exec_venv
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    # when:

    ret_val: str = env_ctx.state_graph.eval_state(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
    )

    # then:

    assert ret_val == proto_code_abs_file_path


@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
)
def test_py_exec_venv_no_arg(
    mock_state_args_parsed,
    mock_state_input_py_exec_arg_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            CommandArg.name_py_exec.value: PythonExecutable.py_exec_venv.name,
            CommandArg.name_proto_code.value: None,
        },
    )
    mock_state_input_py_exec_arg_loaded.return_value = PythonExecutable.py_exec_venv
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    # when/then:

    with pytest.raises(AssertionError) as exc_info:
        env_ctx.state_graph.eval_state(
            EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
        )

    assert "is not specified at" in str(exc_info.value)


@patch(f"{primer_kernel.__name__}.is_venv")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_arg_loaded.__name__}._eval_state_once"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}._eval_state_once"
)
def test_py_exec_arbitrary_not_in_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_arg_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    mock_is_venv,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_input_proto_code_file_abs_path_eval_finalized,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            CommandArg.name_py_exec.value: PythonExecutable.py_exec_arbitrary.name,
        },
    )
    mock_state_input_py_exec_arg_loaded.return_value = (
        PythonExecutable.py_exec_arbitrary
    )
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    mock_is_venv.return_value = False

    # when:

    ret_val: str = env_ctx.state_graph.eval_state(
        EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
    )

    # then:

    assert ret_val == primer_kernel.__file__
