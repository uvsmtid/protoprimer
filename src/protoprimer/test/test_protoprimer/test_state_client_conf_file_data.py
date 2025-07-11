import json
import os
from unittest.mock import patch

from local_test import (
    assert_test_module_name_embeds_str,
    BasePyfakefsTestClass,
)
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_path,
    Bootstrapper_state_client_dir_path_configured,
    ConfConstPrimer,
    EnvContext,
    EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(EnvState.state_client_conf_file_data.name)

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_path.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_path_exists(
        self,
        mock_state_client_conf_file_path,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_dir_path_configured.return_value = mock_client_dir
        state_client_conf_file_path = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_path.return_value = state_client_conf_file_path
        self.fs.create_file(
            state_client_conf_file_path,
            contents=json.dumps({}),
        )

        # when:
        self.assertTrue(os.path.isfile(state_client_conf_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data.name)

        # then:
        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_dir_path_configured.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_path.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_path_missing(
        self,
        mock_state_client_conf_file_path,
        mock_state_client_dir_path_configured,
    ):

        # given:
        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_dir_path_configured.return_value = mock_client_dir
        state_client_conf_file_path = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_path.return_value = state_client_conf_file_path

        # when:
        self.assertFalse(os.path.isfile(state_client_conf_file_path))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data.name)

        # then:
        # file created:
        self.assertTrue(os.path.isfile(state_client_conf_file_path))
