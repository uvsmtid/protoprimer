import tempfile

from protoprimer.primer_kernel import (
    Bootstrapper_state_command_executed,
    EnvContext,
    EnvState,
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
                EnvState.state_local_venv_dir_abs_path_inited.name,
                EnvState.state_local_cache_dir_abs_path_inited.name,
            ],
            state_name=self.state_activated_venv_shell_started,
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        # Start the shell regardless of `ParsedArg.name_command`:
        self.start_interactive_shell = True

        return super()._eval_state_once()
