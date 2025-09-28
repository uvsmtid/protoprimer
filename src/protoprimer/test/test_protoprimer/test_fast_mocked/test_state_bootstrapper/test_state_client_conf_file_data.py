import json
import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_states_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized,
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
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_state_primer_conf_client_file_abs_path_eval_finalized_exists(
        self,
        mock_state_primer_conf_client_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_file_data.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_primer_conf_client_file_abs_path_eval_finalized.return_value = (
            state_primer_conf_client_file_abs_path_eval_finalized
        )
        self.fs.create_file(
            state_primer_conf_client_file_abs_path_eval_finalized,
            contents=json.dumps({}),
        )

        # when:

        self.assertTrue(
            os.path.isfile(state_primer_conf_client_file_abs_path_eval_finalized)
        )
        self.env_ctx.state_graph.eval_state(EnvState.state_client_conf_file_data.name)

        # then:

        # no exception happens

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized.__name__}.eval_own_state"
    )
    def test_state_primer_conf_client_file_abs_path_eval_finalized_missing(
        self,
        mock_state_primer_conf_client_file_abs_path_eval_finalized,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_conf_file_data.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)
        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            mock_client_dir,
            ConfConstPrimer.default_client_conf_file_rel_path,
        )
        mock_state_primer_conf_client_file_abs_path_eval_finalized.return_value = (
            state_primer_conf_client_file_abs_path_eval_finalized
        )

        self.assertFalse(
            os.path.isfile(state_primer_conf_client_file_abs_path_eval_finalized)
        )

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_conf_file_data.name
            )

        # then:

        self.assertIn("does not exists", str(ctx.exception))
