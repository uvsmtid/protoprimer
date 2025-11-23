from __future__ import annotations

import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_env_conf_file_data_loaded,
    Bootstrapper_state_merged_local_cache_dir_abs_path_eval_finalized,
    Bootstrapper_state_merged_required_python_file_abs_path_eval_finalized,
    Bootstrapper_state_reinstall_triggered,
    EnvContext,
    EnvState,
    EnvVar,
    PackageDriverPip,
    PackageDriverType,
    PackageDriverUv,
)


class TestEnvContext(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.fs.create_file("/usr/bin/python", contents="foo")

    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvContext.__name__)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_required_python_file_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.eval_own_state",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/tmp",
    )
    @patch("subprocess.check_call")
    def test_init_default(
        self, mock_check_call, mock_cache, mock_conf, mock_reinstall, mock_python
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_inited.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverUv)

    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value: PackageDriverType.driver_uv.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_required_python_file_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.eval_own_state",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/tmp",
    )
    @patch("subprocess.check_call")
    def test_init_with_uv(
        self, mock_check_call, mock_cache, mock_conf, mock_reinstall, mock_python
    ):
        # given:
        self.fs.create_file("/tmp/venv/uv.venv/bin/uv", contents="foo")
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_inited.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverUv)

    @patch.dict(
        os.environ,
        {
            EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value: PackageDriverType.driver_pip.name,
        },
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_required_python_file_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/usr/bin/python",
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_reinstall_triggered.__name__}.eval_own_state",
        return_value=False,
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_env_conf_file_data_loaded.__name__}.eval_own_state",
        return_value={},
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_merged_local_cache_dir_abs_path_eval_finalized.__name__}.eval_own_state",
        return_value="/tmp",
    )
    def test_init_without_uv(self, mock_cache, mock_conf, mock_reinstall, mock_python):
        # given:
        # when:
        env_ctx = EnvContext()
        package_driver = env_ctx.state_graph.eval_state(
            EnvState.state_package_driver_inited.name
        )
        # then:
        assert isinstance(package_driver, PackageDriverPip)
