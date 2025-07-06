import os
from unittest.mock import patch

from local_test import (
    assert_test_module_name_embeds_str,
    BasePyfakefsTestClass,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_dir_path_configured,
    Bootstrapper_state_py_exec_selected,
    EnvContext,
    EnvState,
    PythonExecutable,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_protoprimer_package_installed.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_selected.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.install_editable_package",
    )
    def test_state_client_conf_file_path_exists(
        self,
        mock_install_editable_package,
        mock_state_py_exec_selected,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_selected.return_value = PythonExecutable.py_exec_venv

        mock_state_client_dir_path_configured.return_value = mock_client_dir

        for distrib_name in [
            "local_repo",
            "local_test",
            "protoprimer",
        ]:
            self.fs.create_file(
                os.path.join(
                    mock_client_dir,
                    "src",
                    distrib_name,
                    "setup.py",
                )
            )

        # when:
        self.env_ctx.bootstrap_state(EnvState.state_protoprimer_package_installed.name)

        # then:
        for distrib_name in [
            "local_repo",
            "local_test",
            "protoprimer",
        ]:
            mock_install_editable_package.assert_any_call(
                os.path.join(
                    mock_client_dir,
                    "src",
                    distrib_name,
                ),
                [],
            )
        self.assertEqual(
            3,
            mock_install_editable_package.call_count,
        )
