from __future__ import annotations

import logging
import os
import subprocess
import sys

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    EnvContext,
    EnvState,
    TargetState,
    ValueType,
)

logger = logging.getLogger()


# noinspection PyPep8Naming
class Bootstrapper_state_pre_commit_configured(AbstractCachingStateNode[int]):

    state_pre_commit_configured = "state_pre_commit_configured"

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                TargetState.target_proto_bootstrap_completed.value.name,
                EnvState.state_global_conf_file_abs_path_inited.name,
            ],
            state_name=self.state_pre_commit_configured,
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_global_conf_file_abs_path_inited = self.eval_parent_state(
            EnvState.state_global_conf_file_abs_path_inited.name
        )
        client_conf_dir_path = os.path.dirname(state_global_conf_file_abs_path_inited)
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
        return 0
