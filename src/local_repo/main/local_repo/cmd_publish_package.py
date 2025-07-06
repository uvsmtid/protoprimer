# !/usr/bin/env python3

# Publish artifacts to pypi.org.

# It is expected to be run under activated `venv`.

# It must be run from repo root:
# ./cmd/publish_package

# A single "atomic" step to make a release:
# - ensure no local modifications
# - ensure commit is published
# - create tag
# - publish package

import os
import re
import shutil
import sys
import venv

from local_repo.sub_proc_util import (
    get_command_code,
    get_command_output,
)


def publish_package(
    client_dir: str,
):
    # Switch to `@/` to avoid creating temporary dirs somewhere else:
    os.chdir(client_dir)

    # Ensure all changes are committed:
    # https://stackoverflow.com/a/3879077/441652
    get_command_code("git update-index --refresh")
    if get_command_code("git diff-index --quiet HEAD --", fail_on_error=False) != 0:
        raise RuntimeError("uncommitted changes")

    # Get the version of `protoprimer` distribution:
    protoprimer_version = None
    version_file_path = os.path.join(
        client_dir,
        "src/protoprimer/main/protoprimer/primer_kernel.py",
    )
    with open(version_file_path, "r") as f:
        match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.M)
        if match:
            protoprimer_version = match.group(1)

    if not protoprimer_version:
        raise RuntimeError(f"Could not find version in {version_file_path}")

    # TODO: use logging:
    print(f"INFO: `protoprimer_version` [{protoprimer_version}]", file=sys.stderr)

    # Determine if it is a dev version (which relaxes many checks):
    is_dev_version: bool
    if re.match(r"^\d+\.\d+\.\d+\.dev\d+$", protoprimer_version):
        print(f"INFO: dev version pattern: {protoprimer_version}", file=sys.stderr)
        is_dev_version = True
    elif re.match(r"^\d+\.\d+\.\d+$", protoprimer_version):
        print(f"INFO: release version pattern: {protoprimer_version}", file=sys.stderr)
        is_dev_version = False
    else:
        raise RuntimeError(f"unrecognized version pattern: {protoprimer_version}")

    print(f"INFO: is_dev_version: {is_dev_version}", file=sys.stderr)

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
        if is_dev_version:
            print(
                f"WARN: current HEAD is not in {git_main_remote}/{git_main_branch}",
                file=sys.stderr,
            )
        else:
            raise RuntimeError(
                f"current HEAD is not in {git_main_remote}/{git_main_branch}"
            )
    else:
        print(
            f"INFO: current HEAD is in {git_main_remote}/{git_main_branch}",
            file=sys.stderr,
        )

    git_tag = get_command_output("git describe --tags")
    print(f"INFO: curr git_tag: {git_tag}", file=sys.stderr)

    # Versions has to be prefixed with `v` in tag:
    if f"v{protoprimer_version}" != git_tag:
        git_tag = f"v{protoprimer_version}"
        if not is_dev_version:
            # Append `.final` for the non-dev (release) version to make a tag:
            git_tag = f"{git_tag}.final"

        print(f"INFO: next git_tag: {git_tag}", file=sys.stderr)

        # Note:
        # *   unsigned unannotated tags appear "Verified" in GitHub
        # *   unsigned annotated does not appear "Verified" in GitHub
        # Create unannotated tag:
        get_command_code(f"git tag {git_tag}")

    else:
        # Matching tag already exists - either already released, or something is wrong.
        # It can be fixed by removing the tag, but the user has to do it consciously.
        raise RuntimeError(f"tag already exits: {git_tag}")

    # Push to remote only if it is a non-dev version:
    if is_dev_version:
        print(f"WARN: tag is not pushed to remote: {git_tag}", file=sys.stderr)
    else:
        print(f"INFO: tag is about to be pushed to remote: {git_tag}", file=sys.stderr)
        get_command_code(f'git push "{git_main_remote}" "{git_tag}"')

    # Switch to `build_dir`:
    build_dir = os.path.join(
        client_dir,
        "src/protoprimer",
    )
    os.chdir(build_dir)

    # Clean up previously built packages:
    dist_dir = os.path.join(
        build_dir,
        "dist",
    )
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    # Create temporary `venv` for twine (do not pollute `venv` used for `protoprimer`):
    twine_venv_path = os.path.join(
        build_dir,
        "venv.twine",
    )
    if os.path.exists(twine_venv_path):
        shutil.rmtree(twine_venv_path)
    venv_builder = venv.EnvBuilder(with_pip=True)
    venv_builder.create(twine_venv_path)

    twine_pip = os.path.join(
        twine_venv_path,
        "bin",
        "pip",
    )
    get_command_code(f"{twine_pip} install setuptools")
    get_command_code(f"{twine_pip} install twine")

    # The following are the staps found in the majority of the web resources.
    twine_python = os.path.join(
        twine_venv_path,
        "bin",
        "python",
    )
    setup_py_path = os.path.join(
        build_dir,
        "setup.py",
    )
    get_command_code(f"{twine_python} {setup_py_path} sdist --verbose")

    twine_command_path = os.path.join(
        twine_venv_path,
        "bin",
        "twine",
    )
    dist_file = os.path.join(
        dist_dir,
        f"protoprimer-{protoprimer_version}.tar.gz",
    )
    # This will prompt for login credentials:
    get_command_code(f"{twine_command_path} upload --verbose {dist_file}")

    # Switch back to `client_dir`:
    os.chdir(client_dir)

    # Change the version to non-release-able to force user to change it later:
    # Equivalent of: sed --in-place
    with open(version_file_path, "r") as f:
        content = f.read()
    new_content = content.replace(
        protoprimer_version, f"WRONG_TO_BE_FIXED.{protoprimer_version}"
    )
    with open(version_file_path, "w") as f:
        f.write(new_content)
