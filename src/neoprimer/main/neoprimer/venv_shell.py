import os

from protoprimer.primer_kernel import (
    AbstractCachingStateBootstrapper,
    ConfConstGeneral,
    create_temp_file,
    EnvContext,
    EnvState,
    logger,
    PythonExecutable,
    StateValueType,
)


# noinspection PyPep8Naming
class Bootstrapper_state_activated_venv_shell_started(
    AbstractCachingStateBootstrapper[bool]
):

    state_activated_venv_shell_started = "state_activated_venv_shell_started"

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                EnvState.state_py_exec_updated_proto_kernel_code.name,
                EnvState.state_local_venv_dir_path_finalized.name,
            ],
            env_state=self.state_activated_venv_shell_started,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_proto_kernel_code = self.bootstrap_parent_state(
            EnvState.state_py_exec_updated_proto_kernel_code.name
        )

        # TODO: this should be the last executable here:
        assert (
            state_py_exec_updated_proto_kernel_code
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        state_local_venv_dir_path_finalized = self.bootstrap_parent_state(
            EnvState.state_local_venv_dir_path_finalized.name
        )

        venv_path_to_activate = os.path.join(
            state_local_venv_dir_path_finalized,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

        temp_file = create_temp_file()
        temp_file.write(f"source ~/.bashrc && source {venv_path_to_activate}")
        temp_file.flush()
        file_path = temp_file.name
        logger.info(f"file_path: {file_path}")
        os.execv(
            # TODO: get path automatically:
            "/usr/bin/bash",
            [
                "bash",
                "--init-file",
                file_path,
            ],
        )

        # noinspection PyUnreachableCode
        return True
