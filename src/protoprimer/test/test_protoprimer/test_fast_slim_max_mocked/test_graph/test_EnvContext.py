from __future__ import annotations

import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.case_condition import requires_max_python
from local_test.mock_subprocess import mock_get_python_version_by_current
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data_loaded,
    Bootstrapper_state_env_conf_file_data_loaded,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_reinstall_triggered,
    Bootstrapper_state_required_python_file_abs_path_inited,
    EnvContext,
    EnvState,
    EnvVar,
    PackageDriverPip,
    PackageDriverType,
    PackageDriverUv,
    StateNode,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
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
    @patch("subprocess.check_call")
    @requires_max_python
    def test_init_default(
        self,
        mock_check_call,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_required_python_file_abs_path_inited,
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_prepared.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverUv)

    @patch("sys.argv", ["script_name"])
    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value: PackageDriverType.driver_uv.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.get_python_version",
        new=mock_get_python_version_by_current,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
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
    @patch("subprocess.check_call")
    @requires_max_python
    def test_init_with_uv(
        self,
        mock_check_call,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_required_python_file_abs_path_inited,
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_prepared.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverUv)

    @patch("sys.argv", ["script_name"])
    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value: PackageDriverType.driver_pip.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.get_python_version",
        new=mock_get_python_version_by_current,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_required_python_file_abs_path_inited.__name__}.{StateNode.eval_own_state.__name__}",
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
    def test_init_without_uv(
        self,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_env_conf_file_data_loaded,
        mock_state_client_conf_file_data_loaded,
        mock_state_reinstall_triggered,
        mock_state_required_python_file_abs_path_inited,
    ):
        # given:
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_prepared.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverPip)
