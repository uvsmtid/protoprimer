from __future__ import annotations

import argparse
import os
import pathlib
import sys

from local_contract_compatibility.baseline_config import read_baseline_commit_names
from local_contract_compatibility.mode_id import ModeId
from local_contract_compatibility.old_entry_on_new_proto import run_old_entry_on_new_proto
from local_contract_compatibility.old_proto_on_new_venv import run_old_proto_on_new_venv
from local_contract_compatibility.old_tests_on_new_changes import run_old_tests_on_new_changes
from metaprimer.script_lib import configure_script
from protoprimer.primer_kernel import EnvState


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    derived_data = configure_script(script_basename=os.path.basename(sys.argv[0]))
    ref_root_abs_path = pathlib.Path(derived_data[EnvState.state_ref_root_dir_abs_path_inited.name])
    scratch_dir_abs_path = pathlib.Path(derived_data[EnvState.state_local_tmp_dir_abs_path_inited.name]) / "local_contract_compatibility"

    if parsed_args.commit_name:
        commit_names = [parsed_args.commit_name]
    else:
        commit_names = read_baseline_commit_names(ref_root_abs_path, parsed_args.package_name)

    exit_code = 0
    for commit_name in commit_names:
        if parsed_args.mode_id == ModeId.new_tests_on_new_changes.value:
            raise NotImplementedError(f"mode [{parsed_args.mode_id}] is not run by the runner: it is defined as running `pytest` normally")
        elif parsed_args.mode_id == ModeId.old_tests_on_new_changes.value:
            mode_exit_code = run_old_tests_on_new_changes(
                ref_root_abs_path,
                parsed_args.package_name,
                commit_name,
                scratch_dir_abs_path,
                parsed_args.pytest_args,
            )
        elif parsed_args.mode_id == ModeId.old_proto_on_new_venv.value:
            mode_exit_code = run_old_proto_on_new_venv(
                ref_root_abs_path,
                parsed_args.package_name,
                commit_name,
                parsed_args.pytest_args,
            )
        elif parsed_args.mode_id == ModeId.old_entry_on_new_proto.value:
            mode_exit_code = run_old_entry_on_new_proto(
                ref_root_abs_path,
                parsed_args.package_name,
                commit_name,
                parsed_args.pytest_args,
            )
        else:
            raise ValueError(f"unknown mode [{parsed_args.mode_id}]")
        exit_code = max(exit_code, mode_exit_code)
    sys.exit(exit_code)


def init_arg_parser():
    arg_parser = argparse.ArgumentParser(description="Runs old contract tests (of baseline commit names) on new changes.")
    arg_parser.add_argument(
        "--package_name",
        required=True,
        help="Package name under `src/`, e.g. `protoprimer`.",
    )
    arg_parser.add_argument(
        "--commit_name",
        help="Run for this commit name only (default: all `baseline_commit_names` from `pyproject.toml`).",
    )
    arg_parser.add_argument(
        "--mode_id",
        required=True,
        choices=[mode_id.value for mode_id in ModeId],
        help=(f"Compatibility mode to run (only `{ModeId.old_tests_on_new_changes.value}`, " f"`{ModeId.old_proto_on_new_venv.value}` and `{ModeId.old_entry_on_new_proto.value}` are run by the runner; `{ModeId.new_tests_on_new_changes.value}` is plain `pytest`)."),
    )
    arg_parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Extra `pytest` args (after `--`).",
    )
    return arg_parser
