from __future__ import annotations

import logging

from neoprimer.venv_shell import Bootstrapper_state_activated_venv_shell_started
from protoprimer.primer_kernel import (
    EnvContext,
    main,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


def customize_env_context():
    """
    See UC_10_80_27_57.extend_dag.md
    """

    env_ctx = EnvContext()

    env_ctx.state_graph.register_node(
        Bootstrapper_state_activated_venv_shell_started(env_ctx)
    )

    env_ctx.default_target = (
        Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
    )

    return env_ctx


if __name__ == "__main__":
    custom_main()
