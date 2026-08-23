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
    arg_parser_instance.add_argument(
        "-c",
        "--link_check",
        action="store_true",
        help="Fail the build if `linkcheck` finds a broken link.",
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

    source_dir = project_root / "doc"
    build_dir = project_root / "doc" / "build"

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

    linkcheck_dir = project_root / "doc" / "build_linkcheck"

    linkcheck_command_args = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        "linkcheck",
        str(source_dir),
        str(linkcheck_dir),
    ]

    print(f"running command: {' '.join(linkcheck_command_args)}")

    linkcheck_result = subprocess.run(linkcheck_command_args, check=False)

    shutil.rmtree(linkcheck_dir)

    if linkcheck_result.returncode != 0:
        if parsed_arguments.link_check:
            raise subprocess.CalledProcessError(
                linkcheck_result.returncode,
                linkcheck_command_args,
            )
        else:
            print(f"WARNING: `linkcheck` found broken links")

    root_url = (build_dir / "index.html").as_uri()
    print(f"open in browser: {root_url}")
