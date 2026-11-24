import argparse
import os
import types
from unittest.mock import patch

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    _BaseNode_state_selected_env_dir_rel_path,
    _Factory_state_args_parsed,
    _Factory_state_selected_env_dir_rel_path_inited,
    _Node_state_selected_env_dir_rel_path_inited_is_app,
    _Node_state_selected_env_dir_rel_path_inited_not_is_app,
    _Node_state_client_conf_file_data_loaded,
    _Node_state_ref_root_dir_abs_path_inited,
    _ContextBuilder,
    _EnvState,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):
    """
    The default env is not a part of the selection (see `FT_03_31_63_70.environment_selection.md`):
    the state is only set by an explicit arg (and is `None` otherwise).
    """

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = (
            _ContextBuilder()
            #
            .entry_func(primer_kernel._EntryFunc.func_boot_env)
            .is_app(True)
            .build_context()
        )
        self.mock_ref_root = abs_path("/mock_ref_root")
        self.fs.create_dir(self.mock_ref_root)
        # By default, there is no env selector configured:
        patcher = patch(f"{primer_kernel.__name__}.{_Node_state_client_conf_file_data_loaded.__name__}.create_state_node")
        self.mock_state_client_conf_file_data_loaded = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {}

    def _given_arg(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
        arg_value,
    ) -> None:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_selected_env_dir_rel_path_inited.name,
        )
        mock_state_ref_root_dir_abs_path_inited.return_value.eval_own_state.return_value = self.mock_ref_root
        mock_state_args_parsed.return_value.eval_own_state.return_value = argparse.Namespace(**{primer_kernel._ParsedArg.name_selected_env_dir.value: arg_value})

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(_EnvState.state_selected_env_dir_rel_path_inited.name)

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_success_when_arg_is_present_and_rel_to_cwd(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        arg_value = "my_env_dir_from_arg"
        # Create it inside ref_root, and CWD will be ref_root
        os.chdir(self.mock_ref_root)
        self.fs.create_dir(arg_value)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertEqual(result, arg_value)

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_success_when_arg_is_present_and_rel_to_ref_root(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(abs_path("/"))  # change cwd to something else
        arg_value = "my_env_dir_from_arg"
        self.fs.create_dir(os.path.join(self.mock_ref_root, arg_value))
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertEqual(result, arg_value)

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_none_when_arg_is_absent(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, None)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then: the default env (if any) is not a selection
        self.assertIsNone(result)

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_failure_when_path_is_not_a_dir(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        self.fs.create_file("not_a_dir")
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, "not_a_dir")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIn("is relative to neither", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_failure_when_path_is_outside_ref_root(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        arg_value = abs_path("/abs/path/outside/ref_root")
        self.fs.create_dir(arg_value)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIn("is not under", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_success_when_abs_path_is_inside_ref_root(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        arg_value_rel = "my_env"
        arg_value_abs = os.path.join(self.mock_ref_root, arg_value_rel)
        self.fs.create_dir(arg_value_abs)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value_abs)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertEqual(result, arg_value_rel)

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_failure_when_path_does_not_exist(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, "missing_dir")

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIn("is relative to neither", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_success_when_path_leads_to_a_dir(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        self.fs.create_dir("valid_dir")
        self.fs.create_symlink("symlink_to_dir", "valid_dir")
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, "symlink_to_dir")

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertEqual(result, "symlink_to_dir")

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_failure_when_abs_path_is_not_a_dir(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        arg_value = abs_path("/abs/path/not_a_dir")
        self.fs.create_file(arg_value)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIn(
            f"`{primer_kernel._PathName.path_selected_env.value}` [{arg_value}] must be a dir.",
            str(ctx.exception),
        )

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_success_when_arg_is_present_and_sub_dir_to_ref_root_but_rel_to_curr_dir(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        arg_value = "my_env_dir_from_arg"
        mock_cwd = os.path.join(self.mock_ref_root, "subdir")
        self.fs.create_dir(mock_cwd)
        os.chdir(mock_cwd)
        self.fs.create_dir(arg_value)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)

        # when:
        result = self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertEqual(result, os.path.join("subdir", arg_value))

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def _given_selector(
        self,
        arg_value,
        selector_code,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ) -> str:
        """
        Configure the selector file with the `selector_code` (and evaluate the state).
        """
        os.chdir(self.mock_ref_root)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, arg_value)
        # Real `import` cannot read the fake file system - only its existence matters here:
        self.fs.create_file(os.path.join(self.mock_ref_root, "env_selector.py"))
        selector_module = types.ModuleType("mock_env_selector_module")
        patcher = patch(f"{primer_kernel.__name__}._import_proto_module", return_value=selector_module)
        patcher.start()
        self.addCleanup(patcher.stop)
        exec(selector_code, selector_module.__dict__)
        self.mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {
            primer_kernel.ConfField.field_env_selector_file_rel_path.value: "env_selector.py",
        }
        return self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

    def test_selector_is_used_when_arg_is_absent(self):
        # given:
        self.fs.create_dir(os.path.join(self.mock_ref_root, "selected_env"))

        # when:
        result = self._given_selector(None, "def select_env_dir_rel_path():\n    return 'selected_env'\n")

        # then:
        self.assertEqual(result, "selected_env")

    def test_arg_overrides_selector(self):
        # given:
        self.fs.create_dir(os.path.join(self.mock_ref_root, "arg_env"))

        # when: the selector would fail if called:
        result = self._given_selector("arg_env", "def select_env_dir_rel_path():\n    raise RuntimeError('must not be called')\n")

        # then:
        self.assertEqual(result, "arg_env")

    def test_none_when_selector_returns_none(self):
        # when:
        result = self._given_selector(None, "def select_env_dir_rel_path():\n    return None\n")

        # then:
        self.assertIsNone(result)

    def test_failure_when_selector_returns_missing_dir(self):
        # when:
        with self.assertRaises(AssertionError) as ctx:
            self._given_selector(None, "def select_env_dir_rel_path():\n    return 'missing_dir'\n")

        # then:
        self.assertIn("is relative to neither", str(ctx.exception))

    def test_failure_when_selector_returns_not_str(self):
        # when:
        with self.assertRaises(AssertionError) as ctx:
            self._given_selector(None, "def select_env_dir_rel_path():\n    return 5\n")

        # then:
        self.assertIn("must return `str` or `None`", str(ctx.exception))

    def test_failure_when_selector_has_no_function(self):
        # when:
        with self.assertRaises(AssertionError) as ctx:
            self._given_selector(None, "x = 1\n")

        # then:
        self.assertIn("does not define `select_env_dir_rel_path`", str(ctx.exception))

    @patch(f"{primer_kernel.__name__}.{_Node_state_ref_root_dir_abs_path_inited.__name__}.create_state_node")
    @patch(f"{primer_kernel.__name__}.{_Factory_state_args_parsed.__name__}.create_state_node")
    def test_failure_when_selector_file_is_missing(
        self,
        mock_state_args_parsed,
        mock_state_ref_root_dir_abs_path_inited,
    ):
        # given:
        os.chdir(self.mock_ref_root)
        self._given_arg(mock_state_args_parsed, mock_state_ref_root_dir_abs_path_inited, None)
        self.mock_state_client_conf_file_data_loaded.return_value.eval_own_state.return_value = {
            primer_kernel.ConfField.field_env_selector_file_rel_path.value: "missing_selector.py",
        }

        # when:
        with self.assertRaises(AssertionError) as ctx:
            self.env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIn("which does not exist", str(ctx.exception))

    # noinspection PyMethodMayBeStatic
    def test_factory_selects_node_by_is_app(self):
        for is_app, entry_func, expected_node_class in [
            (True, primer_kernel._EntryFunc.func_boot_env, _Node_state_selected_env_dir_rel_path_inited_is_app),
            (False, primer_kernel._EntryFunc.func_call_lib, _Node_state_selected_env_dir_rel_path_inited_not_is_app),
            (False, primer_kernel._EntryFunc.func_start_app, _Node_state_selected_env_dir_rel_path_inited_not_is_app),
        ]:
            with self.subTest(is_app=is_app, entry_func=entry_func):
                env_ctx = _ContextBuilder().entry_func(entry_func).is_app(is_app).build_context()
                state_node = _Factory_state_selected_env_dir_rel_path_inited(env_ctx).create_state_node()
                self.assertIs(type(state_node), expected_node_class)

    def test_none_when_not_is_app(self):
        # given: no CLI args are processed outside of `_is_app` (`FT_77_15_06_50.dynamic_DAG.md`)
        env_ctx = _ContextBuilder().entry_func(primer_kernel._EntryFunc.func_call_lib).is_app(False).build_context()

        # when:
        result = env_ctx.eval_state(_EnvState.state_selected_env_dir_rel_path_inited.name)

        # then:
        self.assertIsNone(result)

    # noinspection PyMethodMayBeStatic
    def test_base_node_hook_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            _BaseNode_state_selected_env_dir_rel_path._select_env_conf_dir_any_path(None)
