# !/usr/bin/env python3
# Publish artifacts to an artifact repository (pypi.org by default).
# It is expected to be run under activated `venv`.
# It must be run from the repo root:
# ./cmd/publish_package -h
# A single "atomic" step to make a release:
# - ensure no local modifications
# - ensure the commit is published
# - create tag
# - publish package

import argparse
import enum
import logging
import os
import re
import shutil
import sys
import venv
from typing import (
    Optional,
)

from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)
from protoprimer.primer_kernel import (
    TopDir,
    configure_default_file_log_handler,
    configure_default_stderr_log_handler,
    reconfigure_file_log_handler,
    reconfigure_stderr_log_handler,
)

logger: logging.Logger = logging.getLogger()


def custom_main():
    publish_package(
        # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
        #       Get ref_root from `protoprimer` config (as a lib) instead:
        client_dir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(str(__file__)))))),
        script_basename=os.path.basename(sys.argv[0]),
    )


def publish_package(
    client_dir: str,
    script_basename: str,
):
    parsed_args = init_arg_parser().parse_args()

    # UC_81_50_97_17.reuse_logger.md:
    if reconfigure_stderr_log_handler(logging.INFO) is None:
        configure_default_stderr_log_handler(logging.INFO)

    if reconfigure_file_log_handler(logging.INFO) is None:
        configure_default_file_log_handler(
            # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
            #       Get `log` directory from `protoprimer` config:
            log_file_abs_path=os.path.join(
                client_dir,
                TopDir.dir_log.value,
                f"{script_basename}.log",
            ),
            log_level=logging.INFO,
        )

    logger.info(f"client_dir: {client_dir}")

    _publish_package(
        client_dir=client_dir,
        package_name=parsed_args.package_name,
        repository_url=parsed_args.repository_url,
        no_tag=parsed_args.no_tag or parsed_args.dry_run,
        allow_dirty=parsed_args.allow_dirty,
        dry_run=parsed_args.dry_run,
    )


class DistribPackage(enum.Enum):

    package_metaprimer = "metaprimer"
    package_protoprimer = "protoprimer"
    package_dummy_private = "dummy_private"


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Publish given package to pypi.org",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "package_name",
        type=str,
        choices=[distrib_package.value for distrib_package in DistribPackage],
        help=f"Select package name.",
    )
    arg_parser.add_argument(
        "--repository_url",
        type=str,
        default=None,
        help="Repository URL for twine upload.",
    )
    arg_parser.add_argument(
        "--no_tag",
        action="store_true",
        default=False,
        help="Do not create or push git tag.",
    )
    arg_parser.add_argument(
        "--allow_dirty",
        action="store_true",
        default=False,
        help="Allow publishing with uncommitted changes.",
    )
    arg_parser.add_argument(
        "--dry_run",
        action="store_true",
        default=False,
        help="Build package but skip upload and tagging (implies --no_tag).",
    )
    return arg_parser


def get_tag_name(
    package_name: str,
    distrib_version: str,
) -> str:
    return f"{package_name}-v{distrib_version}"


def create_and_push_tag(
    distrib_version: str,
    git_main_remote: str,
    git_tag: str,
    is_dev_version: bool,
    package_name: str,
):
    # Versions have to be prefixed with `v` in tags:
    if get_tag_name(package_name, distrib_version) != git_tag:
        git_tag = get_tag_name(package_name, distrib_version)
        if not is_dev_version:
            # Append `.final` for the non-dev (release) version to make a tag:
            git_tag = f"{git_tag}.final"

        logger.info(f"next git_tag: {git_tag}")

        # Note:
        # *   unsigned unannotated tags appear "Verified" in GitHub
        # *   unsigned annotated does not appear "Verified" in GitHub
        # Create unannotated tag:
        get_command_code(f"git tag {git_tag}")

    else:
        # Matching tag already exists - either already released, or something is wrong.
        # It can be fixed by removing the tag, but the user has to do it consciously.
        raise RuntimeError(f"tag already exists: {git_tag}")

    # Push to remote only if it is a non-dev version:
    if is_dev_version:
        logger.warning(f"tag is not pushed to remote: {git_tag}")
    else:
        logger.info(f"tag is about to be pushed to remote: {git_tag}")
        get_command_code(f'git push "{git_main_remote}" "{git_tag}"')


def _publish_package(
    client_dir: str,
    package_name: str,
    repository_url: Optional[str],
    no_tag: bool,
    allow_dirty: bool,
    dry_run: bool,
):
    # Switch to `@/` to avoid creating temporary dirs somewhere else:
    os.chdir(client_dir)

    # Ensure all changes are committed:
    # https://stackoverflow.com/a/3879077/441652
    if not allow_dirty:
        get_command_code("git update-index --refresh")
        if get_command_code("git diff-index --quiet HEAD --", fail_on_error=False) != 0:
            raise RuntimeError("uncommitted changes")

    package_name_to_dir: dict[str, str] = {
        DistribPackage.package_metaprimer.value: "metaprimer",
        DistribPackage.package_protoprimer.value: "protoprimer",
        DistribPackage.package_dummy_private.value: "dummy_private",
    }

    package_dir_basename = package_name_to_dir[package_name]

    # Get the version of distribution:
    distrib_version = None
    version_file_path = os.path.join(
        client_dir,
        f"src/{package_dir_basename}/pyproject.toml",
    )
    with open(version_file_path, "r") as f:
        match = re.search(r"^version\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.M)
        if match:
            distrib_version = str(match.group(1))

    if not distrib_version:
        raise RuntimeError(f"Could not find version in {version_file_path}")

    logger.info(f"`distrib_version` [{distrib_version}]")

    # Determine if it is a dev version (which relaxes many checks):
    is_dev_version: bool
    if re.match(r"^\d+\.\d+\.\d+\.dev\d+$", distrib_version):
        logger.info(f"dev version pattern: {distrib_version}")
        is_dev_version = True
    elif re.match(r"^\d+\.\d+\.\d+$", distrib_version):
        logger.info(f"release version pattern: {distrib_version}")
        is_dev_version = False
    else:
        raise RuntimeError(f"unrecognized version pattern: {distrib_version}")

    logger.info(f"is_dev_version: {is_dev_version}")

    # Fetch from upstream:
    git_main_remote = "origin"
    get_command_code(f"git fetch {git_main_remote}")

    # Check if the current commit is in the main branch:
    git_main_branch = "main"
    if (
        get_command_code(
            f"git merge-base --is-ancestor HEAD {git_main_remote}/{git_main_branch}",
            fail_on_error=False,
        )
        != 0
    ):
        if dry_run or package_name == DistribPackage.package_dummy_private.value or is_dev_version:
            logger.warning(f"current HEAD is not in {git_main_remote}/{git_main_branch}")
        else:
            raise RuntimeError(f"current HEAD is not in {git_main_remote}/{git_main_branch}")
    else:
        logger.info(f"current HEAD is in {git_main_remote}/{git_main_branch}")

    if not no_tag:
        git_tag = get_command_output("git describe --tags")
        logger.info(f"curr git_tag: {git_tag}")
        assert isinstance(distrib_version, str)
        create_and_push_tag(
            distrib_version,
            git_main_remote,
            git_tag,
            is_dev_version,
            package_name,
        )

    # Switch to `build_dir`:
    build_dir = os.path.join(
        client_dir,
        f"src/{package_dir_basename}",
    )
    os.chdir(build_dir)

    # Clean up previously built packages:
    dist_dir = os.path.join(
        build_dir,
        "dist",
    )
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    logger.info(f"Python version: {sys.version}")

    # Create temporary `venv` for the build tools (do not pollute `venv` used for the project):
    build_venv_path = os.path.join(
        build_dir,
        "venv.twine",
    )
    if os.path.exists(build_venv_path):
        shutil.rmtree(build_venv_path)
    venv_builder = venv.EnvBuilder(
        with_pip=True,
        symlinks=True,
    )
    venv_builder.create(build_venv_path)

    build_pip_path = os.path.join(
        build_venv_path,
        "bin",
        "pip",
    )
    get_command_code(f"{build_pip_path} install setuptools")
    get_command_code(f"{build_pip_path} install build")
    get_command_code(f"{build_pip_path} install twine")

    # See: FT_17_41_51_83.private_artifact_repo.md:
    get_command_code(f"{build_pip_path} install keyring")
    get_command_code(f"{build_pip_path} install keyrings.google-artifactregistry-auth")

    # The following are the steps found in the majority of the web resources.
    build_python_path = os.path.join(
        build_venv_path,
        "bin",
        "python",
    )
    get_command_code(f"{build_python_path} -m build --sdist --verbose {build_dir}")

    twine_command_path = os.path.join(
        build_venv_path,
        "bin",
        "twine",
    )
    dist_file = os.path.join(
        dist_dir,
        f"{package_name}-{distrib_version}.tar.gz",
    )
    if dry_run:
        logger.info(f"dry_run: skipping upload of {dist_file}")
    else:
        # This will prompt for login credentials:
        if repository_url:
            # See: FT_17_41_51_83.private_artifact_repo.md:
            get_command_code(f"{twine_command_path} upload --verbose --repository-url {repository_url} {dist_file}")
        else:
            get_command_code(f"{twine_command_path} upload --verbose {dist_file}")

    # Switch back to `client_dir`:
    os.chdir(client_dir)

    if not dry_run:
        # Change the version to non-release-able to force the user to change it later:
        # Equivalent of: sed --in-place
        with open(version_file_path, "r") as f:
            content = f.read()
        new_content = content.replace(distrib_version, f"TODO_INCREASE_VERSION.{distrib_version}")
        with open(version_file_path, "w") as f:
            f.write(new_content)
