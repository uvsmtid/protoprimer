from __future__ import annotations

import enum
import logging

from metaprimer.pre_commit import (
    _Node_state_pre_commit_configured,
)
from protoprimer.primer_kernel import (
    _ContextBuilder,
    _EntryFunc,
    _run_process,
)

logger = logging.getLogger()


def custom_main():
    _run_process(customize_env_context())


class CustomEnvState(enum.Enum):

    state_pre_commit_configured = _Node_state_pre_commit_configured


def customize_env_context():
    """
    See UC_10_80_27_57.extend_DAG.md
    """

    env_ctx = (
        _ContextBuilder()
        .entry_func(_EntryFunc.func_boot_env)
        .is_app(True)
        .forced_final_state(CustomEnvState.state_pre_commit_configured.name)
        #
        .build_context()
    )

    env_ctx.register_factory(
        _Node_state_pre_commit_configured._state_name(),
        _Node_state_pre_commit_configured,
    )

    return env_ctx


if __name__ == "__main__":
    custom_main()
