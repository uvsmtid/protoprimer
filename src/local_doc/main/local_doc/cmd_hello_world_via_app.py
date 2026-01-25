# FT_93_57_03_75.app_vs_lib.md: see also `cmd_hello_world_via_lib.py`
from __future__ import annotations

import enum
import logging

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    EnvContext,
    app_main,
    TargetState,
    ValueType,
)

logger = logging.getLogger()


def custom_main():
    app_main(customize_env_context)


# noinspection PyPep8Naming
class Bootstrapper_state_hello_world_printed(AbstractCachingStateNode[int]):

    # TODO: Make it simpler: can this be simplified?
    #       Need to find a way to simplify specifying the state name and their dependencies.

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                TargetState.target_proto_bootstrap_completed.value.name,
            ],
            state_name=CustomEnvState.state_hello_world_printed.name,
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        print("Hello, world!")

        return 0


class CustomEnvState(enum.Enum):

    state_hello_world_printed = Bootstrapper_state_hello_world_printed


def customize_env_context():
    """
    See UC_10_80_27_57.extend_DAG.md
    """

    # TODO: Make it simpler: have a builder? At least env_ctx.populate_dependencies() does not have to be explicit.

    env_ctx = EnvContext()

    env_ctx.state_graph.register_node(Bootstrapper_state_hello_world_printed(env_ctx))

    env_ctx.final_state = CustomEnvState.state_hello_world_printed.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
