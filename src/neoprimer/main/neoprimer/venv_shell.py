import argparse
import logging

from protoprimer.primer_kernel import (
    _get_shell_driver,
    AbstractCachingStateNode,
    EnvState,
    ParsedArg,
    ShellDriverBase,
    StateStride,
    trivial_factory,
)


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_activated_venv_shell_started(AbstractCachingStateNode[int]):

    _state_name = staticmethod(lambda: "state_activated_venv_shell_started")

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_stride_src_updated_reached.name,
        ]
    )

    def _eval_state_once(
        self,
    ) -> int:

        state_default_stderr_log_handler_configured: logging.Handler = self.eval_parent_state(EnvState.state_default_stderr_log_handler_configured.name)

        assert self.env_ctx.get_stride().value >= StateStride.stride_src_updated.value

        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        state_local_cache_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_cache_dir_abs_path_inited.name,
        )

        command_line: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_command.value,
            None,
        )

        shell_driver: ShellDriverBase = _get_shell_driver(state_local_cache_dir_abs_path_inited)

        return shell_driver.run_shell(
            # Start the shell regardless of `ParsedArg.name_command`:
            True,
            command_line,
            state_default_stderr_log_handler_configured,
            state_local_venv_dir_abs_path_inited,
        )
