import os

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    ConfConstGeneral,
    create_temp_file,
    EnvContext,
    EnvState,
    logger,
    PythonExecutable,
    StateValueType,
)


# noinspection PyPep8Naming
class Bootstrapper_state_activated_venv_shell_started(AbstractCachingStateNode[bool]):

    state_activated_venv_shell_started = "state_activated_venv_shell_started"

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_py_exec_updated_proto_code.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
            ],
            state_name=self.state_activated_venv_shell_started,
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_proto_code = self.eval_parent_state(
            EnvState.state_py_exec_updated_proto_code.name
        )

        # TODO: this should be the last executable here:
        assert (
            state_py_exec_updated_proto_code
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )

        venv_path_to_activate = os.path.join(
            state_env_local_venv_dir_abs_path_eval_finalized,
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
