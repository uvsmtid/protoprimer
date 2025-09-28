import argparse
import os
from unittest.mock import patch

import pytest

from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_input_py_exec_var_loaded,
    Bootstrapper_state_input_wizard_stage_arg_loaded,
    ConfConstInput,
    EnvContext,
    EnvState,
    ParsedArg,
    PythonExecutable,
    WizardStage,
)


@pytest.fixture
def env_ctx():
    return EnvContext()


def test_relationship():
    assert_test_module_name_embeds_str(EnvState.state_py_exec_arbitrary_reached.name)


@patch.dict(
    f"{os.__name__}.environ",
    {
        ConfConstInput.ext_env_var_VIRTUAL_ENV: "/path/to/venv",
        ConfConstInput.ext_env_var_PATH: "/path/to/venv/bin:/usr/bin",
    },
    clear=True,
)
@patch(f"{primer_kernel.__name__}.warn_if_non_venv_package_installed")
@patch(f"{primer_kernel.__name__}.get_path_to_curr_python")
@patch(f"{primer_kernel.__name__}.get_path_to_base_python")
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_py_exec_unknown_in_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_var_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    mock_switch_python,
    mock_get_path_to_base_python,
    mock_get_path_to_curr_python,
    mock_warn_if_non_venv_package_installed,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_py_exec_arbitrary_reached.name,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_wizard_stage.value: WizardStage.wizard_started.name,
            ParsedArg.name_start_id.value: "mock_start_id",
            ParsedArg.name_reinstall.value: False,
        },
    )
    mock_state_input_py_exec_var_loaded.return_value = PythonExecutable.py_exec_unknown
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    mock_get_path_to_curr_python.return_value = "/path/to/venv/bin/python"
    mock_get_path_to_base_python.return_value = "/usr/bin/python"

    # when:

    env_ctx.state_graph.eval_state(EnvState.state_py_exec_arbitrary_reached.name)

    # then:

    mock_switch_python.assert_called_once_with(
        curr_py_exec=PythonExecutable.py_exec_unknown,
        curr_python_path=mock_get_path_to_curr_python.return_value,
        next_py_exec=PythonExecutable.py_exec_arbitrary,
        next_python_path=mock_get_path_to_base_python.return_value,
        start_id="mock_start_id",
        proto_code_abs_file_path=None,
        wizard_stage=WizardStage.wizard_started,
        required_environ={"PATH": "/usr/bin"},
    )


@patch.dict(f"{os.__name__}.environ", {}, clear=True)
@patch(f"{primer_kernel.__name__}.switch_python")
@patch(f"{primer_kernel.__name__}.warn_if_non_venv_package_installed")
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_wizard_stage_arg_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_input_py_exec_var_loaded.__name__}.eval_own_state"
)
@patch(
    f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
)
def test_py_exec_unknown_not_in_venv(
    mock_state_args_parsed,
    mock_state_input_py_exec_var_loaded,
    mock_state_input_wizard_stage_arg_loaded,
    mock_warn_if_non_venv_package_installed,
    mock_switch_python,
    env_ctx,
):
    # given:

    assert_parent_states_mocked(
        env_ctx,
        EnvState.state_py_exec_arbitrary_reached.name,
    )

    mock_state_args_parsed.return_value = argparse.Namespace(
        **{
            ParsedArg.name_start_id.value: "mock_start_id",
            ParsedArg.name_reinstall.value: False,
        },
    )
    mock_state_input_py_exec_var_loaded.return_value = PythonExecutable.py_exec_unknown
    mock_state_input_wizard_stage_arg_loaded.return_value = WizardStage.wizard_started

    # when:

    env_ctx.state_graph.eval_state(EnvState.state_py_exec_arbitrary_reached.name)

    # then:
    mock_switch_python.assert_called_once()
