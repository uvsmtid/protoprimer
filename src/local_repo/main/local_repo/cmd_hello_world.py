from __future__ import annotations

import enum
import logging

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    EnvContext,
    main,
    StateValueType,
    TargetState,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


# noinspection PyPep8Naming
class Bootstrapper_state_hello_world_printed(AbstractCachingStateNode[bool]):

    # TODO: Make it simpler: can this be simplified?
    #       Need to find a way to simplify specifying the state name and their dependencies.

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                TargetState.target_full_proto_bootstrap,
            ],
            state_name=CustomEnvState.state_hello_world_printed.name,
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        # TODO: Make it simpler: it does not have to be explicit loop. It should probably be default behavior.

        # Bootstrap all dependencies:
        for state_name in self.parent_states:
            self.eval_parent_state(state_name)

        print("Hello, world!")

        return True


class CustomEnvState(enum.Enum):

    state_hello_world_printed = Bootstrapper_state_hello_world_printed


def customize_env_context():
    """
    See UC_10_80_27_57.extend_dag.md
    """

    # TODO: Make it simpler: have a builder? At least env_ctx.populate_dependencies() does not have to be explicit.

    env_ctx = EnvContext()

    env_ctx.state_graph.register_node(Bootstrapper_state_hello_world_printed(env_ctx))

    env_ctx.default_target = CustomEnvState.state_hello_world_printed.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
