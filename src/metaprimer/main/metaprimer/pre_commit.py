from __future__ import annotations

import logging
import os
import subprocess
import sys

from protoprimer.primer_kernel import (
    _AbstractCachingStateNode,
    _EnvState,
    _TargetState,
    _trivial_factory,
    _ValueType,
)

logger = logging.getLogger()


# noinspection PyPep8Naming
@_trivial_factory
class _Node_state_pre_commit_configured(_AbstractCachingStateNode[int]):

    _state_name = staticmethod(lambda: "state_pre_commit_configured")

    _parent_states = staticmethod(
        lambda: [
            _TargetState.target_proto_bootstrap_completed.value.name,
            _EnvState.state_global_conf_file_abs_path_inited.name,
            _EnvState.state_ref_root_dir_abs_path_inited.name,
        ]
    )

    def _eval_state_once(
        self,
    ) -> _ValueType:

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(_EnvState.state_ref_root_dir_abs_path_inited.name)

        is_git_repo: bool = False
        try:
            # It succeeds only if under `git` repo (and `git` installed):
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "--is-inside-work-tree",
                ],
                cwd=state_ref_root_dir_abs_path_inited,
            )
            is_git_repo = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info(f"ref root dir [{state_ref_root_dir_abs_path_inited}] is not under a `git` repository, skipping pre-commit...")

        if not is_git_repo:
            return 0

        state_global_conf_file_abs_path_inited: str = self.eval_parent_state(_EnvState.state_global_conf_file_abs_path_inited.name)
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
