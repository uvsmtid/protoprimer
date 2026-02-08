from __future__ import annotations

import argparse
import enum
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger()


# FT_84_11_73_28: supported python versions:
class PythonVersion(enum.Enum):

    python_min = "3.7"
    python_max = "3.14"


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    current_dir = str(Path.cwd())

    container_commands_list = [
        # Copy sources to avoid modifying originals:
        "mkdir /tmp/test_ws",
        "cp -r . /tmp/test_ws",
        "cd /tmp/test_ws",
        # Remove leftovers:
        "rm -f lconf",
        "rm -rf venv",
        #
        "apt-get update",
        "apt-get install -y git",
        # TODO: FT_48_62_07_98.config_format.md:
        #       After moving to `*.py` config files, add comment to ref back to this script why this config exists:
        # TODO: TODO_03_47_85_89.implement_python_selection.md:
        f"./prime --env dst/test_python_{parsed_args.python}",
    ]
    if not parsed_args.shell:
        container_commands_list.append("./venv/bin/pytest")
    container_commands = " && ".join(container_commands_list)
    if parsed_args.test_file:
        container_commands = f"{container_commands} {parsed_args.test_file}"

    selected_python_version = PythonVersion[f"python_{parsed_args.python}"].value
    logger.info(f"Starting docker with python version: {selected_python_version}")

    docker_env_vars = []
    if parsed_args.ci:
        docker_env_vars.extend(["-e", "CI=true"])

    docker_command = [
        "docker",
        "run",
        "--rm",
    ]
    if parsed_args.shell:
        docker_command.extend(["-it"])
    docker_command.extend(
        [
            "-v",
            f"{current_dir}:/app:z",
            "-w",
            "/app",
            *docker_env_vars,
            f"python:{selected_python_version}-slim",
        ]
    )

    if parsed_args.shell:
        docker_command.extend(["bash", "-c", f"{container_commands} && bash"])
    else:
        docker_command.extend(["bash", "-c", container_commands])

    sub_proc = subprocess.run(docker_command, check=True)


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Run tests with different versions of `python` via `docker`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--python",
        type=str,
        choices=[v.name.replace("python_", "") for v in PythonVersion],
        default=PythonVersion.python_min.name.replace("python_", ""),
        help="Selected `python` version to use for testing.",
    )
    arg_parser.add_argument(
        "--ci",
        action="store_true",
        help="Run tests in CI mode (sets CI=true inside docker container).",
    )
    arg_parser.add_argument(
        "--test_file",
        type=str,
        help="Run a specific test file instead of all of them.",
    )
    arg_parser.add_argument(
        "--shell",
        action="store_true",
        help="Jump into the shell of the docker container instead of running pytest.",
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
