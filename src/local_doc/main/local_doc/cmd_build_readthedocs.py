import argparse
import os
import re
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path


class BuildMode(str, Enum):
    single_page = "single_page"
    multi_page = "multi_page"


# Sphinx defaults `linkcheck_rate_limit_timeout` to 300s, which looks like a hang:
default_rate_limit_timeout_seconds = 10

# Excluded from checks the same way `conf.py` excludes them from the build:
reference_link_excluded_dir_names = {"untracked_notes", "task_ref", "dev_note", "draft_doc"}

code_fence_regex = re.compile(r"```.*?```", re.DOTALL)
reference_link_usage_regex = re.compile(r"\[[^\]\n]*\]\[([^\]\n]+)\]")
reference_link_definition_regex = re.compile(r"^\[([^\]\n]+)\]:\s*\S", re.MULTILINE)


def find_broken_reference_links(source_dir):
    """
    MyST silently renders an undefined `[text][label]` reference as literal
    text (no link, no warning) instead of failing the build, so broken
    reference-style links have to be found by scanning the Markdown sources.
    """
    broken_link_reports = []
    for markdown_file_path in sorted(source_dir.rglob("*.md")):
        if reference_link_excluded_dir_names & set(markdown_file_path.relative_to(source_dir).parts):
            continue
        markdown_text = markdown_file_path.read_text()
        code_free_text = code_fence_regex.sub("", markdown_text)
        defined_labels = set(reference_link_definition_regex.findall(code_free_text))
        used_labels = set(reference_link_usage_regex.findall(code_free_text))
        for missing_label in sorted(used_labels - defined_labels):
            broken_link_reports.append(f"{markdown_file_path}: undefined reference link label: [{missing_label}]")
    return broken_link_reports


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
        "--check_links",
        action="store_true",
        help="Fail the build if `linkcheck` finds a broken link.",
    )
    arg_parser_instance.add_argument(
        "-t",
        "--rate_limit_timeout",
        type=int,
        default=default_rate_limit_timeout_seconds,
        help="Max seconds `linkcheck` retries a single rate-limited link before giving up " f"(default: {default_rate_limit_timeout_seconds}).",
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

    linkcheck_dir = project_root / "doc" / "linkcheck"

    if linkcheck_dir.exists():
        shutil.rmtree(linkcheck_dir)

    broken_reference_links = find_broken_reference_links(source_dir)
    if broken_reference_links:
        for broken_link_report in broken_reference_links:
            print(f"WARNING: broken reference link: {broken_link_report}")
        if parsed_arguments.check_links:
            raise RuntimeError(f"found {len(broken_reference_links)} broken reference link(s)")

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

    # `sphinx-build -D` can't override a `float` config, so use an env var instead:
    linkcheck_env_vars = os.environ | {
        "PROTOPRIMER_LINKCHECK_RATE_LIMIT_TIMEOUT": str(parsed_arguments.rate_limit_timeout),
    }

    linkcheck_result = subprocess.run(
        linkcheck_command_args,
        env=linkcheck_env_vars,
        check=False,
    )

    if linkcheck_result.returncode != 0:
        if parsed_arguments.check_links:
            raise subprocess.CalledProcessError(
                linkcheck_result.returncode,
                linkcheck_command_args,
            )
        else:
            print(f"WARNING: `linkcheck` found broken links")

    if parsed_arguments.build_mode == BuildMode.single_page:
        builder_name = "singlehtml"
    elif parsed_arguments.build_mode == BuildMode.multi_page:
        builder_name = "html"
    else:
        raise ValueError(f"unknown build mode: {parsed_arguments.build_mode}")

    build_command_args = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        builder_name,
        str(source_dir),
        str(build_dir),
    ]

    if parsed_arguments.check_links:
        build_command_args += ["-W", "--keep-going"]

    print(f"running command: {' '.join(build_command_args)}")

    # `sphinx-build` should be available inside the `venv`:
    subprocess.run(
        build_command_args,
        check=True,
    )

    root_url = (build_dir / "index.html").as_uri()
    print(f"open in browser: {root_url}")
