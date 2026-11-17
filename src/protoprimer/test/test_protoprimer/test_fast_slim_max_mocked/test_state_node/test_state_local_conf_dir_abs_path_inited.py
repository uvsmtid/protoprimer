import os
import sys
import typing
from unittest.mock import patch

from local_repo.cmd_prime_env import customize_env_context
from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _BaseNode_state_local_conf_dir_abs_path_inited,
    _Factory_state_local_conf_dir_abs_path_inited,
    _Node_state_client_conf_file_data_loaded,
    _NodeFactory,
    _Node_state_global_conf_dir_abs_path_inited,
    _Node_state_local_conf_dir_abs_path_inited_boot,
    _Node_state_local_conf_dir_abs_path_inited_eval,
    _Node_state_local_conf_dir_abs_path_inited_reset,
    _Node_state_local_conf_dir_abs_path_inited_read,
    _Node_state_ref_root_dir_abs_path_inited,
    _Factory_state_selected_env_dir_rel_path_inited,
    _ConfConstClient,
    _ConfConstInput,
    _ConfConstPrimer,
    ConfField,
    _EnvState,
    _ExecOperation,
    _write_json_file,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()
        patcher = patch(f"{primer_kernel.__name__}.{_Node_state_global_conf_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
        self.mock_state_global_conf_dir_abs_path_inited = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_state_global_conf_dir_abs_path_inited.return_value.eval_own_state.return_value = "/mock_global_conf_dir"

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(_EnvState.state_local_conf_dir_abs_path_inited.name)

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_exists_and_target_dst_dir_unspecified(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        mock_target_dir = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(mock_target_dir)
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            mock_target_dir,
        )
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = mock_target_dir

        # when:

        with patch.object(sys, "argv", test_args):
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        # no exception happens

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_exists_and_target_dst_dir_matches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        self.fs.create_dir(target_dst_dir_path)
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            target_dst_dir_path,
        )
        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = target_dst_dir_path

        # when:

        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        # no exception happens

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_failure_when_conf_symlink_exists_but_target_dst_dir_mismatches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )
        actual_target_dir = os.path.join(
            "actual_target_dir",
        )
        expected_target_dir = os.path.join(
            "expected_target_dir",
        )
        state_local_conf_dir_abs_path_inited = os.path.join(mock_client_dir, "lconf")
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: os.path.basename(state_local_conf_dir_abs_path_inited)}
        self.fs.create_dir(actual_target_dir)
        self.fs.create_dir(expected_target_dir)
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            actual_target_dir,
        )

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = expected_target_dir

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_failure_when_conf_symlink_is_not_directory(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )
        mock_not_a_dir = os.path.join(
            "file",
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_file(mock_not_a_dir)
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            mock_not_a_dir,
        )
        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = mock_not_a_dir

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertIn("is not a directory", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_failure_when_conf_is_not_symlink(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(state_local_conf_dir_abs_path_inited)
        client_script_basename = "client_script.py"
        test_args = [
            client_script_basename,
        ]

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = "some_dir"

        # when:

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(AssertionError) as ctx:
                self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertIn("is not a symlink", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_is_created_if_it_is_missing_and_target_dir_is_given(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        self.env_ctx._exec_operation = _ExecOperation.op_boot
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )
        target_dst_dir_path = os.path.join(
            "target_dir",
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path)

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = target_dst_dir_path

        # when:

        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertTrue(os.path.islink(state_local_conf_dir_abs_path_inited))
        self.assertEqual(
            os.readlink(state_local_conf_dir_abs_path_inited),
            target_dst_dir_path,
        )

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_is_created_with_normalized_target(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        self.env_ctx._exec_operation = _ExecOperation.op_boot
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        target_dst_dir_path_non_normalized = "target_dir/"
        target_dst_dir_path_normalized = "target_dir"
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        self.fs.create_dir(target_dst_dir_path_normalized)

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = target_dst_dir_path_non_normalized

        # when:

        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertTrue(os.path.islink(state_local_conf_dir_abs_path_inited))
        self.assertEqual(
            os.readlink(state_local_conf_dir_abs_path_inited),
            target_dst_dir_path_normalized,
        )

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_local_env_conf_dir_is_none(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_ref_root = "/mock_ref_root"
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_ref_root
        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = None
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {}  # no symlink, no default

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then: nothing selected, nothing persisted, no default => global config dir
        self.assertEqual(result, "/mock_global_conf_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_is_nested_and_target_matches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):
        """
        Regression test for a symlink nested under `ref_root` (e.g. `conf/env`):
        the on-disk symlink target is relative to the symlink's own dir (`dst/default_env`),
        while `state_selected_env_dir_rel_path_inited` is relative to `ref_root` (`conf/dst/default_env`).
        These must be reconciled before comparing, not compared raw.
        """

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        nested_conf_link_rel_path = os.path.join("conf", "env")
        # `ref_root`-relative target (as it is provided/configured):
        ref_root_rel_target_dir = os.path.join("conf", "dst", "default_env")
        # Same target, but relative to the symlink's own dir (`conf/`) - what must end up on disk:
        symlink_dir_rel_target_dir = os.path.join("dst", "default_env")

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: nested_conf_link_rel_path}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            nested_conf_link_rel_path,
        )
        self.fs.create_dir(os.path.join(mock_client_dir, "conf", "dst", "default_env"))
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            symlink_dir_rel_target_dir,
        )

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = ref_root_rel_target_dir

        # when:

        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        # no exception happens

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_failure_when_conf_symlink_is_nested_and_target_mismatches(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):

        # given:

        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        nested_conf_link_rel_path = os.path.join("conf", "env")
        ref_root_rel_target_dir = os.path.join("conf", "dst", "default_env")
        actual_symlink_dir_rel_target_dir = os.path.join("dst", "other_env")

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: nested_conf_link_rel_path}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            nested_conf_link_rel_path,
        )
        self.fs.create_dir(os.path.join(mock_client_dir, "conf", "dst", "default_env"))
        self.fs.create_dir(os.path.join(mock_client_dir, "conf", "dst", "other_env"))
        self.fs.create_symlink(
            state_local_conf_dir_abs_path_inited,
            actual_symlink_dir_rel_target_dir,
        )

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = ref_root_rel_target_dir

        # when:

        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_success_when_conf_symlink_is_nested_and_created_with_dir_relative_target(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
    ):
        """
        When the symlink itself lives in a subdir of `ref_root`, the target written on disk
        must be relative to that subdir, not to `ref_root`.
        """

        # given:

        self.env_ctx._exec_operation = _ExecOperation.op_boot
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        primer_conf_data = {
            ConfField.field_ref_root_dir_rel_path.value: ".",
            ConfField.field_global_conf_dir_rel_path.value: _ConfConstPrimer.default_client_conf_dir_rel_path,
        }
        _write_json_file(
            os.path.join(mock_client_dir, _ConfConstInput.default_file_basename_conf_primer),
            primer_conf_data,
        )

        nested_conf_link_rel_path = os.path.join("conf", "env")
        ref_root_rel_target_dir = os.path.join("conf", "dst", "default_env")
        symlink_dir_rel_target_dir = os.path.join("dst", "default_env")

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {ConfField.field_local_conf_symlink_rel_path.value: nested_conf_link_rel_path}

        state_local_conf_dir_abs_path_inited = os.path.join(
            mock_client_dir,
            nested_conf_link_rel_path,
        )
        self.fs.create_dir(os.path.join(mock_client_dir, "conf", "dst", "default_env"))

        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = ref_root_rel_target_dir

        # when:

        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:

        self.assertTrue(os.path.islink(state_local_conf_dir_abs_path_inited))
        self.assertEqual(
            os.readlink(state_local_conf_dir_abs_path_inited),
            symlink_dir_rel_target_dir,
        )

    def _given_env_with_persisted_symlink(
        self,
        mock_state_selected_env_dir_rel_path_inited,
        mock_state_ref_root_dir_abs_path_inited,
        mock_state_client_conf_file_data_loaded,
        exec_operation: typing.Optional[_ExecOperation],
        selected_env_dir_rel_path: typing.Optional[str],
        persisted_env_dir_rel_path: typing.Optional[str],
        default_env_dir_rel_path: typing.Optional[str] = None,
    ) -> str:
        """
        Set up `ref_root` with `selected` and `persisted` env dirs (the latter is `None` if the symlink is missing).

        Returns the symlink abs path.
        """
        # NOTE: the node is instantiated (and cached) lazily, set the exec operation before:
        self.env_ctx._exec_operation = exec_operation
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_local_conf_dir_abs_path_inited.name,
        )

        mock_client_dir = "/mock_client_dir"
        # NOTE: idempotent setup (can be called repeatedly in one test):
        if not os.path.exists(mock_client_dir):
            self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        symlink_abs_path = os.path.join(
            mock_client_dir,
            _ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )
        for env_dir_rel_path in [selected_env_dir_rel_path, persisted_env_dir_rel_path, default_env_dir_rel_path]:
            if env_dir_rel_path is not None and not os.path.exists(env_dir_rel_path):
                self.fs.create_dir(env_dir_rel_path)
        if persisted_env_dir_rel_path is not None and not os.path.lexists(symlink_abs_path):
            self.fs.create_symlink(
                symlink_abs_path,
                persisted_env_dir_rel_path,
            )

        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = mock_client_dir
        client_conf_data = {ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name}
        if default_env_dir_rel_path is not None:
            client_conf_data[ConfField.field_default_env_dir_rel_path.value] = default_env_dir_rel_path
        mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = client_conf_data
        mock_state_selected_env_dir_rel_path_inited.return_value.eval_own_state.return_value = selected_env_dir_rel_path
        return symlink_abs_path

    # noinspection PyMethodMayBeStatic
    def test_factory_selects_node_by_exec_operation(self):
        for exec_operation, expected_node_class in [
            (_ExecOperation.op_eval, _Node_state_local_conf_dir_abs_path_inited_eval),
            (_ExecOperation.op_reset, _Node_state_local_conf_dir_abs_path_inited_reset),
            (_ExecOperation.op_boot, _Node_state_local_conf_dir_abs_path_inited_boot),
            (_ExecOperation.op_start, _Node_state_local_conf_dir_abs_path_inited_read),
            (_ExecOperation.op_shell, _Node_state_local_conf_dir_abs_path_inited_read),
            (_ExecOperation.op_wrap, _Node_state_local_conf_dir_abs_path_inited_read),
            (None, _Node_state_local_conf_dir_abs_path_inited_read),
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx._exec_operation = exec_operation
                state_node = _Factory_state_local_conf_dir_abs_path_inited(self.env_ctx).create_state_node()
                self.assertIs(type(state_node), expected_node_class)

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_strict_returns_direct_env_dir_not_symlink_when_persisted_matches(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_boot, "target_dir", "target_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/target_dir")
        self.assertNotEqual(result, symlink_abs_path)

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_strict_creates_symlink_and_returns_direct_env_dir_when_not_persisted(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_boot, "target_dir", None)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/target_dir")
        self.assertEqual(os.readlink(symlink_abs_path), "target_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_strict_fails_on_mismatch_for_ops_which_only_read_persisted_env(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        for exec_operation in [
            _ExecOperation.op_boot,
            _ExecOperation.op_start,
            _ExecOperation.op_shell,
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx = customize_env_context()
                self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, exec_operation, "selected_dir", "persisted_dir")

                with self.assertRaises(AssertionError) as ctx:
                    self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

                self.assertIn("not the same as the provided target", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_reset_overwrites_persisted_symlink_on_mismatch(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_reset, "selected_dir", "persisted_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(os.readlink(symlink_abs_path), "selected_dir")
        self.assertEqual(result, "/mock_client_dir/selected_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_reset_keeps_persisted_symlink_on_match(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_reset, "target_dir", "target_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(os.readlink(symlink_abs_path), "target_dir")
        self.assertEqual(result, "/mock_client_dir/target_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_reset_creates_symlink_when_not_persisted(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_reset, "selected_dir", None)

        # when:
        self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(os.readlink(symlink_abs_path), "selected_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_reset_never_deletes_real_dir_in_place_of_symlink(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_reset, "selected_dir", None)
        self.fs.create_dir(symlink_abs_path)

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertIn("is not a symlink", str(ctx.exception))
        self.assertTrue(os.path.isdir(symlink_abs_path))
        self.assertFalse(os.path.islink(symlink_abs_path))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_eval_ignores_persisted_symlink_on_mismatch(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_eval, "selected_dir", "persisted_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/selected_dir")
        self.assertEqual(os.readlink(symlink_abs_path), "persisted_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_eval_does_not_create_symlink_when_not_persisted(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_eval, "selected_dir", None)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/selected_dir")
        self.assertFalse(os.path.lexists(symlink_abs_path))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_eval_works_when_entry_is_not_a_symlink(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_eval, "selected_dir", None)
        self.fs.create_dir(symlink_abs_path)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/selected_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_nothing_selected_uses_persisted_symlink_value_for_all_ops(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        for exec_operation in [
            _ExecOperation.op_boot,
            _ExecOperation.op_reset,
            _ExecOperation.op_start,
            _ExecOperation.op_shell,
            _ExecOperation.op_wrap,
            _ExecOperation.op_eval,
            None,
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx = customize_env_context()
                symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, exec_operation, None, "persisted_dir", default_env_dir_rel_path="default_dir")

                result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

                # the default is only a fallback - the persisted value wins and the link is untouched:
                self.assertEqual(result, "/mock_client_dir/persisted_dir")
                self.assertEqual(os.readlink(symlink_abs_path), "persisted_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_nothing_selected_nothing_persisted_uses_default_and_only_boot_and_reset_persist_it(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        for exec_operation, expect_link in [
            (_ExecOperation.op_boot, True),
            (_ExecOperation.op_reset, True),
            (_ExecOperation.op_start, False),
            (_ExecOperation.op_shell, False),
            (_ExecOperation.op_wrap, False),
            (_ExecOperation.op_eval, False),
            (None, False),
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx = customize_env_context()
                symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, exec_operation, None, None, default_env_dir_rel_path="default_dir")
                if os.path.lexists(symlink_abs_path):
                    os.remove(symlink_abs_path)

                result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

                self.assertEqual(result, "/mock_client_dir/default_dir")
                self.assertEqual(os.path.islink(symlink_abs_path), expect_link)
                if expect_link:
                    self.assertEqual(os.readlink(symlink_abs_path), "default_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_nothing_selected_nothing_persisted_no_default_uses_global_conf_dir_without_link(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        for exec_operation in [
            _ExecOperation.op_boot,
            _ExecOperation.op_reset,
            _ExecOperation.op_start,
            _ExecOperation.op_eval,
            None,
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx = customize_env_context()
                symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, exec_operation, None, None)
                if os.path.lexists(symlink_abs_path):
                    os.remove(symlink_abs_path)

                result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

                self.assertEqual(result, "/mock_global_conf_dir")
                self.assertFalse(os.path.lexists(symlink_abs_path))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_read_ops_do_not_create_symlink_for_selected_env(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        for exec_operation in [
            _ExecOperation.op_start,
            _ExecOperation.op_shell,
            _ExecOperation.op_wrap,
        ]:
            with self.subTest(exec_operation=exec_operation):
                self.env_ctx = customize_env_context()
                symlink_abs_path = self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, exec_operation, "selected_dir", None)
                if os.path.lexists(symlink_abs_path):
                    os.remove(symlink_abs_path)

                result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

                self.assertEqual(result, "/mock_client_dir/selected_dir")
                self.assertFalse(os.path.lexists(symlink_abs_path))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_selected_env_is_used_when_symlink_is_not_configured(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_boot, "selected_dir", None)
        mock_client_conf.return_value.eval_own_state.return_value = {}

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/selected_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_failure_when_default_env_path_is_absolute(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_boot, None, None)
        mock_client_conf.return_value.eval_own_state.return_value = {
            ConfField.field_local_conf_symlink_rel_path.value: _ConfConstClient.default_dir_rel_path_leap_env_link_name,
            ConfField.field_default_env_dir_rel_path.value: "/abs/default_env",
        }

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertIn("must be a relative path", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_read_outside_of_app_uses_persisted_env_without_comparing_it(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given: `_is_app` is `False` (e.g. `_EntryFunc.func_start_app`), the selected env mismatches the persisted one
        self.env_ctx._is_app = False
        self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_start, "selected_dir", "persisted_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then:
        self.assertEqual(result, "/mock_client_dir/persisted_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_selected_env_dir_rel_path_inited.__name__}.{_NodeFactory.create_state_node.__name__}")
    def test_reset_uses_selected_env_when_symlink_is_not_configured(
        self,
        mock_selected,
        mock_ref_root,
        mock_client_conf,
    ):
        # given:
        self._given_env_with_persisted_symlink(mock_selected, mock_ref_root, mock_client_conf, _ExecOperation.op_reset, "selected_dir", None)
        mock_client_conf.return_value.eval_own_state.return_value = {}

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_local_conf_dir_abs_path_inited.name)

        # then: nothing to persist the env in
        self.assertEqual(result, "/mock_client_dir/selected_dir")

    # noinspection PyMethodMayBeStatic
    def test_base_node_hook_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            _BaseNode_state_local_conf_dir_abs_path_inited._eval_env_dir_abs_path(None, "/ref_root", "dst/env", "/ref_root/lconf")

    # noinspection PyMethodMayBeStatic
    def test_compose_selected_env_dir_abs_path_is_normalized(self):
        self.assertEqual(
            _BaseNode_state_local_conf_dir_abs_path_inited._compose_selected_env_dir_abs_path("/ref_root", "dst/./env/"),
            "/ref_root/dst/env",
        )
        self.assertEqual(
            _BaseNode_state_local_conf_dir_abs_path_inited._compose_selected_env_dir_abs_path("/ref_root", "conf/../dst/env"),
            "/ref_root/dst/env",
        )
