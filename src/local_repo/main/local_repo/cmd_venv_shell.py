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
    env_ctx = EnvContext()

    env_ctx.register_bootstrapper(
        Bootstrapper_state_activated_venv_shell_started(env_ctx)
    )

    env_ctx.populate_dependencies()

    env_ctx.default_target = (
        Bootstrapper_state_activated_venv_shell_started.state_activated_venv_shell_started
    )

    return env_ctx


if __name__ == "__main__":
    custom_main()
