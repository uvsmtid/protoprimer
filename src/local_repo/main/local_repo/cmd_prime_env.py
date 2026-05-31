from __future__ import annotations

import enum
import logging

from metaprimer.pre_commit import (
    Bootstrapper_state_pre_commit_configured,
)
from protoprimer.primer_kernel import (
    ContextBuilder,
    EntryFunc,
    run_process,
)

logger = logging.getLogger()


def custom_main():
    run_process(customize_env_context())


class CustomEnvState(enum.Enum):

    state_pre_commit_configured = Bootstrapper_state_pre_commit_configured


def customize_env_context():
    """
    See UC_10_80_27_57.extend_DAG.md
    """

    env_ctx = (
        ContextBuilder()
        .entry_func(EntryFunc.func_boot_env)
        .is_app(True)
        .final_state(CustomEnvState.state_pre_commit_configured.name)
        #
        .build_context()
    )

    env_ctx.register_factory(
        Bootstrapper_state_pre_commit_configured._state_name(),
        Bootstrapper_state_pre_commit_configured,
    )

    return env_ctx


if __name__ == "__main__":
    custom_main()
