from __future__ import annotations

import logging

from protoprimer.primer_kernel import (
    EnvContext,
    main,
    TargetState,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


def customize_env_context():
    env_ctx = EnvContext()
    # NOTE: This is the only customization here:
    env_ctx.universal_sink = TargetState.target_activated_venv_shell
    return env_ctx


if __name__ == "__main__":
    custom_main()
