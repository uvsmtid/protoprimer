import argparse
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path


class BuildMode(str, Enum):
    single_page = "single_page"
    multi_page = "multi_page"


def init_arg_parser():
    arg_parser_instance = argparse.ArgumentParser(
        description="Builds Sphinx documentation.",
    )
    arg_parser_instance.add_argument(
        "--build_mode",
        type=BuildMode,
        choices=[enum_item.name for enum_item in BuildMode],
        default=BuildMode.multi_page,
        help=f"The build mode for the documentation: {', '.join([e.name for e in BuildMode])}.",
    )
    return arg_parser_instance


def build_readthedocs():
    """
    Builds Sphinx documentation.
    """
    arg_parser_instance = init_arg_parser()
    parsed_arguments = arg_parser_instance.parse_args()

    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       Be able to take it from config API.
    project_root = Path.cwd()

    source_dir = project_root / "doc" / "readthedocs" / "source"
    build_dir = project_root / "doc" / "readthedocs" / "build"

    if build_dir.exists():
        print(f"removing build directory: {build_dir}")
        shutil.rmtree(build_dir)

    if parsed_arguments.build_mode == BuildMode.single_page:
        builder = "singlehtml"
    elif parsed_arguments.build_mode == BuildMode.multi_page:
        builder = "html"
    else:
        raise ValueError(f"unknown build mode: {parsed_arguments.build_mode}")

    command_args = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        builder,
        str(source_dir),
        str(build_dir),
    ]

    print(f"running command: {' '.join(command_args)}")

    # `sphinx-build` should be available inside the `venv`:
    subprocess.run(command_args, check=True)

    root_url = (build_dir / "index.html").as_uri()
    print(f"open in browser: {root_url}")
