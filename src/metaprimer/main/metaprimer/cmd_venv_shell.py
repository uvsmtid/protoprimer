from __future__ import annotations

import logging

from metaprimer.venv_shell import Bootstrapper_state_activated_venv_shell_started
from protoprimer.primer_kernel import (
    proto_main,
    EnvContext,
)

logger = logging.getLogger()


def custom_main():
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       convert from `boot_env` to `start_app` when it can access the config.
    proto_main(customize_env_context)


def customize_env_context():
    """
    See UC_10_80_27_57.extend_DAG.md
    """

    env_ctx = EnvContext()

    env_ctx.state_graph.register_factory(
        Bootstrapper_state_activated_venv_shell_started._state_name(),
        Bootstrapper_state_activated_venv_shell_started(env_ctx),
    )

    # NOTE: It runs instead of `EnvState.state_command_executed` but also supports the `--command` arg.
    env_ctx.final_state = Bootstrapper_state_activated_venv_shell_started._state_name()

    return env_ctx


if __name__ == "__main__":
    custom_main()
