import os
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_client_conf_file_data,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    EnvContext,
    EnvState,
    write_json_file,
)
from test_protoprimer.misc_tools.mock_verifier import assert_parent_states_mocked


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_field_is_present(
        self,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_dir_rel_path_eval_finalized,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        client_conf_file_data = {
            ConfField.field_client_default_target_dir_rel_path.value: "my_env_dir",
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:

        state_client_local_env_dir_rel_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
            )
        )

        # then:

        self.assertEqual(
            state_client_local_env_dir_rel_path_eval_finalized, "my_env_dir"
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_failure_when_field_is_missing(
        self,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_dir_rel_path_eval_finalized,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        client_conf_file_data = {}
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
            )

        # then:

        self.assertIn(
            f"Field `{ConfField.field_client_default_target_dir_rel_path.value}` is [None]",
            str(ctx.exception),
        )

    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_client_conf_file_data.__name__}.eval_own_state"
    )
    def test_success_when_field_is_empty_string(
        self,
        mock_state_client_conf_file_data,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            EnvState.state_client_local_env_dir_rel_path_eval_finalized,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_primer_ref_root_dir_rel_path.value: ".",
            ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
        }
        write_json_file(
            os.path.join(
                mock_client_dir, ConfConstInput.default_file_basename_conf_primer
            ),
            primer_conf_data,
        )

        client_conf_file_data = {
            ConfField.field_client_default_target_dir_rel_path.value: "",
        }
        mock_state_client_conf_file_data.return_value = client_conf_file_data

        # when:

        state_client_local_env_dir_rel_path_eval_finalized = (
            self.env_ctx.state_graph.eval_state(
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
            )
        )

        # then:

        self.assertEqual(state_client_local_env_dir_rel_path_eval_finalized, "")
