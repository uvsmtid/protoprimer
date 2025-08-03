from __future__ import annotations

import enum
import logging

from protoprimer.primer_kernel import (
    AbstractCachingStateBootstrapper,
    EnvContext,
    main,
    StateValueType,
    TargetState,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


# noinspection PyPep8Naming
class Bootstrapper_state_hello_world_printed(AbstractCachingStateBootstrapper[bool]):

    # TODO: Make it simpler: can this be simplified?
    #       Need to find a way to simplify specifying the state name and their dependencies.

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                TargetState.target_full_proto_bootstrap,
            ],
            env_state=CustomEnvState.state_hello_world_printed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        # TODO: Make it simpler: it does not have to be explicit loop. It should probably be default behavior.

        # Bootstrap all dependencies:
        for env_state in self.state_parents:
            self.bootstrap_parent_state(env_state)

        print("Hello, world!")

        return True


class CustomEnvState(enum.Enum):

    state_hello_world_printed = Bootstrapper_state_hello_world_printed


def customize_env_context():

    # TODO: Make it simpler: have a builder? At least env_ctx.populate_dependencies() does not have to be explicit.

    env_ctx = EnvContext()

    env_ctx.register_bootstrapper(Bootstrapper_state_hello_world_printed(env_ctx))

    env_ctx.populate_dependencies()

    env_ctx.default_target = CustomEnvState.state_hello_world_printed.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
