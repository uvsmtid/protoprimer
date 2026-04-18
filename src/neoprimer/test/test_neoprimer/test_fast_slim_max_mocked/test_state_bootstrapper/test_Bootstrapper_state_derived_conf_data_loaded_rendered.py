from unittest.mock import patch

from local_test.mock_verifier import assert_parent_factories_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer import conf_renderer
from neoprimer.cmd_eval_conf import customize_env_context
from neoprimer.conf_renderer import (
    Bootstrapper_state_derived_conf_data_loaded_rendered,
    Bootstrapper_state_env_conf_file_data_loaded_rendered,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_required_python_version_inited,
    Bootstrapper_state_global_conf_dir_abs_path_inited,
    Bootstrapper_state_global_conf_file_abs_path_inited,
    Bootstrapper_state_input_exec_mode_arg_loaded,
    Bootstrapper_state_input_stderr_log_level_eval_finalized,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_local_conf_file_abs_path_inited,
    Bootstrapper_state_local_conf_symlink_abs_path_inited,
    Bootstrapper_state_local_log_dir_abs_path_inited,
    Bootstrapper_state_local_tmp_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_primer_conf_file_abs_path_inited,
    Bootstrapper_state_project_descriptors_inited,
    Bootstrapper_state_proto_code_file_abs_path_inited,
    Bootstrapper_state_ref_root_dir_abs_path_inited,
    Bootstrapper_state_selected_env_dir_rel_path_inited,
    Bootstrapper_state_selected_python_file_abs_path_inited,
    Bootstrapper_state_venv_driver_inited,
    EnvState,
)


def test_relationship():
    assert_test_module_name_embeds_str(Bootstrapper_state_derived_conf_data_loaded_rendered.__name__)


@patch("sys.argv", [""])
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_exec_mode_arg_loaded.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_input_stderr_log_level_eval_finalized.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_proto_code_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_global_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_env_dir_rel_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_symlink_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_conf_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_required_python_version_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_log_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_tmp_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_venv_driver_inited.__name__}.create_state_node")
@patch(f"{primer_kernel.__name__}.{Bootstrapper_state_project_descriptors_inited.__name__}.create_state_node")
@patch(f"{conf_renderer.__name__}.{Bootstrapper_state_env_conf_file_data_loaded_rendered.__name__}.create_state_node")
def test_state_evaluation(
    mock_create_state_env_conf_file_data_loaded_rendered,
    mock_create_state_project_descriptors_inited,
    mock_create_state_venv_driver_inited,
    mock_create_state_local_cache_dir_abs_path_inited,
    mock_create_state_local_tmp_dir_abs_path_inited,
    mock_create_state_local_log_dir_abs_path_inited,
    mock_create_state_local_venv_dir_abs_path_inited,
    mock_create_state_selected_python_file_abs_path_inited,
    mock_create_required_python_version_inited,
    mock_create_state_local_conf_file_abs_path_inited,
    mock_create_state_local_conf_symlink_abs_path_inited,
    mock_create_state_selected_env_dir_rel_path_inited,
    mock_create_state_global_conf_file_abs_path_inited,
    mock_create_state_global_conf_dir_abs_path_inited,
    mock_create_state_ref_root_dir_abs_path_inited,
    mock_create_state_primer_conf_file_abs_path_inited,
    mock_create_state_proto_code_file_abs_path_inited,
    mock_create_state_input_stderr_log_level_eval_finalized,
    mock_create_state_input_exec_mode_arg_loaded,
):

    # given:

    env_ctx = customize_env_context()

    assert_parent_factories_mocked(
        env_ctx,
        Bootstrapper_state_derived_conf_data_loaded_rendered._state_name(),
    )

    mock_create_state_proto_code_file_abs_path_inited.return_value.eval_own_state.return_value = "/mock/proto_code/proto_kernel.json"
    mock_create_state_primer_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "/mock/primer.json"
    mock_create_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/ref_root"
    mock_create_state_global_conf_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/gconf"
    mock_create_state_global_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "/mock/gconf/proto_kernel.json"
    mock_create_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = "envs/default"
    mock_create_state_local_conf_symlink_abs_path_inited.return_value.eval_own_state.return_value = "/mock/ref_root/conf.json"
    mock_create_state_local_conf_file_abs_path_inited.return_value.eval_own_state.return_value = "/mock/envs/default/conf.json"
    mock_create_required_python_version_inited.return_value.eval_own_state.return_value = "3.11"
    mock_create_state_selected_python_file_abs_path_inited.return_value.eval_own_state.return_value = "/usr/bin/python3"
    mock_create_state_local_venv_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/venv"
    mock_create_state_local_log_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/log"
    mock_create_state_local_tmp_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/tmp"
    mock_create_state_local_cache_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock/cache"
    mock_create_state_project_descriptors_inited.return_value.eval_own_state.return_value = []

    # when:

    result = env_ctx.state_graph.eval_state(
        Bootstrapper_state_derived_conf_data_loaded_rendered._state_name(),
        env_ctx,
    )

    # then:

    assert isinstance(result, dict)
    assert EnvState.state_local_venv_dir_abs_path_inited.name in result
    assert EnvState.state_local_cache_dir_abs_path_inited.name in result
    assert EnvState.state_project_descriptors_inited.name in result
    assert result[EnvState.state_local_venv_dir_abs_path_inited.name] == "/mock/venv"
    assert result[EnvState.state_local_cache_dir_abs_path_inited.name] == "/mock/cache"
    assert result[EnvState.state_project_descriptors_inited.name] == []
