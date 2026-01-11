import argparse
import logging
import os
from unittest.mock import patch, ANY

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import assert_parent_states_mocked
from local_test.name_assertion import assert_test_module_name_embeds_str
from neoprimer.cmd_venv_shell import customize_env_context
from neoprimer.venv_shell import Bootstrapper_state_activated_venv_shell_started
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    Bootstrapper_state_args_parsed,
    Bootstrapper_state_default_stderr_log_handler_configured,
    Bootstrapper_state_local_cache_dir_abs_path_inited,
    Bootstrapper_state_local_venv_dir_abs_path_inited,
    Bootstrapper_state_py_exec_updated_proto_code,
    ConfConstGeneral,
    ParsedArg,
    PythonExecutable,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = customize_env_context()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
        )

    @patch("sys.argv", [""])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.write_text_file")
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch.dict(os.environ, {"SHELL": "/path/to/bash"})
    def test_start_bash_shell_with_activated_venv(
        self,
        mock_execve,
        mock_write_text_file,
        mock_state_py_exec_updated_proto_code,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_default_stderr_log_handler_configured,
        mock_state_args_parsed,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started,
        )

        mock_state_default_stderr_log_handler_configured.return_value.level = (
            logging.INFO
        )
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_command.value: None,
            }
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_updated_proto_code.return_value = (
            PythonExecutable.py_exec_updated_proto_code
        )

        mock_state_local_venv_dir_abs_path_inited.return_value = mock_client_dir
        cache_dir = os.path.join(mock_client_dir, "cache")
        mock_state_local_cache_dir_abs_path_inited.return_value = cache_dir
        expected_venv_activate_path = os.path.join(
            mock_state_local_venv_dir_abs_path_inited.return_value,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
        )

        # then:
        init_file_path = os.path.join(cache_dir, "bash", ".bashrc")
        mock_execve.assert_called_once()
        self.assertEqual(mock_execve.call_args[0][0], "/path/to/bash")
        self.assertIn("--init-file", mock_execve.call_args[0][1])
        self.assertIn(init_file_path, mock_execve.call_args[0][1])

        mock_write_text_file.assert_called_once_with(
            init_file_path,
            f"""
# Load user settings if available:
test -f ~/.bashrc && source ~/.bashrc || true
# Activate `venv`:
source {expected_venv_activate_path}
""",
        )

    @patch("sys.argv", [""])
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_args_parsed.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_default_stderr_log_handler_configured.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_venv_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_local_cache_dir_abs_path_inited.__name__}.eval_own_state"
    )
    @patch(
        f"{primer_kernel.__name__}.{Bootstrapper_state_py_exec_updated_proto_code.__name__}.eval_own_state"
    )
    @patch(f"{primer_kernel.__name__}.write_text_file")
    @patch(f"{primer_kernel.__name__}.os.execve")
    @patch.dict(os.environ, {"SHELL": "/path/to/zsh"})
    def test_start_zsh_shell_with_activated_venv(
        self,
        mock_execve,
        mock_write_text_file,
        mock_state_py_exec_updated_proto_code,
        mock_state_local_cache_dir_abs_path_inited,
        mock_state_local_venv_dir_abs_path_inited,
        mock_state_default_stderr_log_handler_configured,
        mock_state_args_parsed,
    ):

        # given:

        assert_parent_states_mocked(
            self.env_ctx,
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started,
        )

        mock_state_default_stderr_log_handler_configured.return_value.level = (
            logging.INFO
        )
        mock_state_args_parsed.return_value = argparse.Namespace(
            **{
                ParsedArg.name_command.value: None,
            }
        )

        mock_client_dir = "/mock_client_dir"
        self.fs.create_dir(mock_client_dir)
        os.chdir(mock_client_dir)

        mock_state_py_exec_updated_proto_code.return_value = (
            PythonExecutable.py_exec_updated_proto_code
        )

        mock_state_local_venv_dir_abs_path_inited.return_value = mock_client_dir
        cache_dir = os.path.join(mock_client_dir, "cache")
        mock_state_local_cache_dir_abs_path_inited.return_value = cache_dir
        expected_venv_activate_path = os.path.join(
            mock_state_local_venv_dir_abs_path_inited.return_value,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # when:

        self.env_ctx.state_graph.eval_state(
            Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
        )

        # then:
        init_file_path = os.path.join(cache_dir, "zsh", ".zshrc")
        mock_execve.assert_called_once()
        self.assertEqual(mock_execve.call_args[0][0], "/path/to/zsh")
        self.assertNotIn("--init-file", mock_execve.call_args[0][1])
        self.assertEqual(
            mock_execve.call_args.args[2]["ZDOTDIR"],
            os.path.dirname(init_file_path),
        )

        mock_write_text_file.assert_called_once_with(
            init_file_path,
            f"""
# Load user settings if available:
test -f ~/.zshrc && source ~/.zshrc || true
# Activate `venv`:
source {expected_venv_activate_path}
""",
        )
