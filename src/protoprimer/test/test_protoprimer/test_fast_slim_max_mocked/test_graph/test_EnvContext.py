from __future__ import annotations

import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.case_condition import is_min_python
from local_test.integrated_helper import test_python_version
from local_test.mock_subprocess import mock_get_python_version_by_current
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_required_python_version_inited,
    Bootstrapper_state_client_conf_file_data_loaded,
    Bootstrapper_state_env_conf_file_data_loaded,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_reinstall_triggered,
    Bootstrapper_state_selected_python_file_abs_path_inited,
    EnvContext,
    EnvState,
    EnvVar,
    StateNode,
    VenvDriverPip,
    VenvDriverType,
    VenvDriverUv,
)


class TestEnvContext(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.create_file("/usr/bin/python", contents="foo")

    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvContext.__name__)

    @patch("sys.argv", ["script_name"])
    @patch(
        f"{primer_kernel.__name__}.get_python_version",
        new=mock_get_python_version_by_current,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_required_python_version_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=test_python_version,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp/venv",
    )
    @patch("subprocess.check_call")
    def test_init_default(
        self,
        mock_check_call,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_required_python_version_inited,
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        venv_driver = env_ctx.state_graph.eval_state(
            EnvState.state_venv_driver_prepared.name
        )
        # then:
        if is_min_python():
            assert isinstance(venv_driver, VenvDriverPip)
        else:
            assert isinstance(venv_driver, VenvDriverUv)

    @patch("sys.argv", ["script_name"])
    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_uv.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.get_python_version",
        new=mock_get_python_version_by_current,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_required_python_version_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=test_python_version,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp/venv",
    )
    @patch("subprocess.check_call")
    def test_init_with_uv(
        self,
        mock_check_call,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_required_python_version_inited,
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        venv_driver = env_ctx.state_graph.eval_state(
            EnvState.state_venv_driver_prepared.name
        )
        # then:
        if is_min_python():
            assert isinstance(venv_driver, VenvDriverPip)
        else:
            assert isinstance(venv_driver, VenvDriverUv)

    @patch("sys.argv", ["script_name"])
    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_pip.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.get_python_version",
        new=mock_get_python_version_by_current,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_required_python_version_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=test_python_version,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_selected_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.{StateNode.eval_own_state.__name__}",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.{StateNode.eval_own_state.__name__}",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
        return_value="/tmp/venv",
    )
    def test_init_without_uv(
        self,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_selected_python_file_abs_path_inited,
        mock_state_required_python_version_inited,
    ):
        # given:
        # when:
        env_ctx = EnvContext()
        venv_driver = env_ctx.state_graph.eval_state(
            EnvState.state_venv_driver_prepared.name
        )
        # then:
        assert isinstance(venv_driver, VenvDriverPip)
