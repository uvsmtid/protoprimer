from __future__ import annotations

import enum
import logging
import os.path
import subprocess

from protoprimer.primer_kernel import (
    AbstractCachingStateBootstrapper,
    EnvContext,
    EnvState,
    install_package,
    main,
    StateValueType,
    TargetState,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


# noinspection PyPep8Naming
class Bootstrapper_state_pre_commit_installed(AbstractCachingStateBootstrapper[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                TargetState.target_full_proto_bootstrap,
            ],
            env_state=CustomEnvState.state_pre_commit_installed.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        # Bootstrap all dependencies:
        for env_state in self.state_parents:
            self.env_ctx.bootstrap_state(env_state)

        install_package(
            "pre-commit",
        )
        return True


# noinspection PyPep8Naming
class Bootstrapper_state_pre_commit_configured(AbstractCachingStateBootstrapper[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            state_parents=[
                CustomEnvState.state_pre_commit_installed.name,
                EnvState.state_client_conf_file_path.name,
            ],
            env_state=CustomEnvState.state_pre_commit_configured.name,
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_pre_commit_installed = self.env_ctx.bootstrap_state(
            CustomEnvState.state_pre_commit_installed.name
        )
        assert state_pre_commit_installed

        state_client_conf_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_client_conf_file_path.name
        )
        client_conf_dir_path = os.path.dirname(state_client_conf_file_path)
        pre_commit_conf_file_path = os.path.join(
            client_conf_dir_path,
            "pre_commit.yaml",
        )
        logger.info(f"pre_commit_conf_file_path: {pre_commit_conf_file_path}")

        subprocess.check_call(
            [
                "pre-commit",
                "install",
                #
                "--hook-type",
                "pre-commit",
                #
                "--config",
                pre_commit_conf_file_path,
            ]
        )
        return True


class CustomEnvState(enum.Enum):

    def __init__(
        self,
        # Default implementation (for reference):
        default_impl,
    ):
        self.default_impl = default_impl

    state_pre_commit_installed = (Bootstrapper_state_pre_commit_installed,)

    state_pre_commit_configured = (Bootstrapper_state_pre_commit_configured,)


def customize_env_context():

    env_ctx = EnvContext()

    env_ctx.register_bootstrapper(Bootstrapper_state_pre_commit_installed(env_ctx))
    env_ctx.register_bootstrapper(Bootstrapper_state_pre_commit_configured(env_ctx))

    env_ctx.populate_dependencies()

    env_ctx.universal_sink = CustomEnvState.state_pre_commit_configured.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
