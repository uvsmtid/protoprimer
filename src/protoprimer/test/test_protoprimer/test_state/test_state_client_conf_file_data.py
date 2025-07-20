import json
import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.base_test_class import BasePyfakefsTestClass
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_abs_path_global,
    Bootstrapper_state_client_ref_dir_abs_path_global,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_ref_dir_abs_path_global.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_abs_path_global.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_abs_path_global_exists(
        self,
        mock_state_client_conf_file_abs_path_global,
        mock_state_client_ref_dir_abs_path_global,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_ref_dir_abs_path_global.return_value = mock_client_dir
        state_client_conf_file_abs_path_global = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_abs_path_global.return_value = (
            state_client_conf_file_abs_path_global
        )
        self.fs.create_file(
            state_client_conf_file_abs_path_global,
            contents=json.dumps({}),
        )

        # when:

        self.assertTrue(os.path.isfile(state_client_conf_file_abs_path_global))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data.name)

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_ref_dir_abs_path_global.__name__}._bootstrap_once"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_abs_path_global.__name__}._bootstrap_once"
    )
    def test_state_client_conf_file_abs_path_global_missing(
        self,
        mock_state_client_conf_file_abs_path_global,
        mock_state_client_ref_dir_abs_path_global,
    ):

        # given:

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        mock_state_client_ref_dir_abs_path_global.return_value = mock_client_dir
        state_client_conf_file_abs_path_global = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_file_rel_path_conf_client,
        )
        mock_state_client_conf_file_abs_path_global.return_value = (
            state_client_conf_file_abs_path_global
        )

        # when:

        self.assertFalse(os.path.isfile(state_client_conf_file_abs_path_global))
        self.env_ctx.bootstrap_state(EnvState.state_client_conf_file_data.name)

        # then:

        # file created:
        self.assertTrue(os.path.isfile(state_client_conf_file_abs_path_global))
