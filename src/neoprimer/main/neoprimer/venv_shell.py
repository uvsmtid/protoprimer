import argparse
import os
import subprocess
import sys

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    Bootstrapper_state_command_executed,
    ConfConstGeneral,
    create_temp_file,
    EnvContext,
    EnvState,
    EnvVar,
    logger,
    ParsedArg,
    PythonExecutable,
    ValueType,
)


# noinspection PyPep8Naming
class Bootstrapper_state_activated_venv_shell_started(
    Bootstrapper_state_command_executed
):

    state_activated_venv_shell_started = "state_activated_venv_shell_started"

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_default_stderr_log_handler_configured.name,
                EnvState.state_py_exec_updated_proto_code.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
            ],
            state_name=self.state_activated_venv_shell_started,
        )

    def _prepare_shell_env(
        self,
    ) -> ValueType:

        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )

        venv_path_to_activate = os.path.join(
            state_env_local_venv_dir_abs_path_eval_finalized,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        # NOTE: Normally, FT_75_87_82_46.entry_script.md starting `venv_shell` sets this env var to
        #       avoid time-consuming installation, so it is removed here before starting the command:
        del os.environ[EnvVar.var_PROTOPRIMER_DO_INSTALL.value]

        # TODO: Move file under configured tmp dir:
        temp_file = create_temp_file()
        temp_file.write(f"source ~/.bashrc && source {venv_path_to_activate}")
        temp_file.flush()
        file_path = temp_file.name
        logger.debug(f"file_path: {file_path}")

        shell_basename: str = os.path.basename(self.shell_abs_path)
        # TODO: To support other shells, need to prepare their equivalents of `--init-file` arg:
        assert shell_basename in ["bash"]

        self.shell_args: list[str] = [
            shell_basename,
            "--init-file",
            file_path,
        ]

        # Start shell regardless of `ParsedArg.name_command`:
        self.start_shell = True
