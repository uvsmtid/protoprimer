from __future__ import annotations

import enum
import logging

from neoprimer.pre_commit import (
    Bootstrapper_state_pre_commit_configured,
)
from protoprimer.primer_kernel import (
    EnvContext,
    main,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


class CustomEnvState(enum.Enum):

    state_pre_commit_configured = Bootstrapper_state_pre_commit_configured


def customize_env_context():
    """
    See UC_10_80_27_57.extend_DAG.md
    """

    env_ctx = EnvContext()

    env_ctx.state_graph.register_node(Bootstrapper_state_pre_commit_configured(env_ctx))

    env_ctx.final_state = CustomEnvState.state_pre_commit_configured.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
