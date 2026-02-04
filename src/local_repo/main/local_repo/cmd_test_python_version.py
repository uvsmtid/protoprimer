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
        "mkdir /tmp/test_ws",
        "cp -r . /tmp/test_ws",
        "cd /tmp/test_ws",
        "rm -f lconf",
        "rm -rf venv",
        "apt-get update",
        "apt-get install -y git",
        "rm -rf /var/lib/apt/lists/*",
        # TODO: After moving to `*.py` config files, add comment to ref back to this script why this config exists:
        "./prime --env dst/test_python_version",
        "./venv/bin/pytest",
    ]
    container_commands = " && ".join(container_commands_list)

    selected_python_version = PythonVersion[f"python_{parsed_args.python}"].value
    logger.info(f"Starting docker with python version: {selected_python_version}")
    docker_command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{current_dir}:/app:z",
        "-w",
        "/app",
        f"python:{selected_python_version}-slim",
        "bash",
        "-c",
        container_commands,
    ]

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
    return arg_parser


if __name__ == "__main__":
    custom_main()
