from __future__ import annotations

import enum
import logging
import os.path
import subprocess
import sys

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
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
class Bootstrapper_state_pre_commit_installed(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                TargetState.target_full_proto_bootstrap,
            ],
            state_name=CustomEnvState.state_pre_commit_installed.name,
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        # Bootstrap all dependencies:
        for state_name in self.parent_states:
            self.eval_parent_state(state_name)

        install_package(
            "pre-commit",
        )
        return True


# noinspection PyPep8Naming
class Bootstrapper_state_pre_commit_configured(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                CustomEnvState.state_pre_commit_installed.name,
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
            ],
            state_name=CustomEnvState.state_pre_commit_configured.name,
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_pre_commit_installed = self.eval_parent_state(
            CustomEnvState.state_pre_commit_installed.name
        )
        assert state_pre_commit_installed

        state_primer_conf_client_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )
        client_conf_dir_path = os.path.dirname(
            state_primer_conf_client_file_abs_path_eval_finalized
        )
        pre_commit_conf_file_path = os.path.join(
            client_conf_dir_path,
            "pre_commit.yaml",
        )
        logger.info(f"pre_commit_conf_file_path: {pre_commit_conf_file_path}")

        path_to_pre_commit = os.path.join(
            os.path.dirname(sys.executable),
            "pre-commit",
        )

        subprocess.check_call(
            [
                path_to_pre_commit,
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

    state_pre_commit_installed = Bootstrapper_state_pre_commit_installed

    state_pre_commit_configured = Bootstrapper_state_pre_commit_configured


def customize_env_context():
    """
    See UC_10_80_27_57.extend_dag.md
    """

    env_ctx = EnvContext()

    env_ctx.state_graph.register_node(Bootstrapper_state_pre_commit_installed(env_ctx))
    env_ctx.state_graph.register_node(Bootstrapper_state_pre_commit_configured(env_ctx))

    env_ctx.default_target = CustomEnvState.state_pre_commit_configured.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
