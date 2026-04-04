from protoprimer.primer_kernel import (
    Bootstrapper_state_command_executed,
    EnvContext,
    EnvState,
    trivial_factory,
)


# noinspection PyPep8Naming
@trivial_factory
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
                EnvState.state_default_stderr_log_handler_configured.name,
                EnvState.state_args_parsed.name,
                EnvState.state_local_venv_dir_abs_path_inited.name,
                EnvState.state_local_cache_dir_abs_path_inited.name,
                EnvState.state_stride_src_updated_reached.name,
            ],
            state_name=self.state_activated_venv_shell_started,
            # Start the shell regardless of `ParsedArg.name_command`:
            start_interactive_shell=True,
        )
