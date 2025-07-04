#!/usr/bin/env bash

# Publish artifacts to pypi.org.

# It is expected to be run under activated `venv`.

# It must be run from repo root:
# ./cmd/publish_package.bash

# A single "atomic" step to make a release:
# - ensure no local modifications
# - ensure commit is published
# - create tag
# - publish package

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# dir_structure: `@/cmd/` -> `@/`:
client_dir="$( dirname "${script_dir}" )"

# Switch to `@/` to avoid creating temporary dirs somewhere else:
cd "${client_dir}" || exit 1

if [[ -z "$VIRTUAL_ENV" ]]
then
    echo "ERROR:venv is not activated"
    exit 1
fi

# Ensure all changes are committed:
# https://stackoverflow.com/a/3879077/441652
git update-index --refresh
if ! git diff-index --quiet HEAD --
then
    echo "ERROR: uncommitted changes" 1>&2
    exit 1
fi

# Get version of `protoprimer` distribution:
protoprimer_version="$( sed -n "s/^__version__ = ['\"]\([^'\"]*\)['\"]/\1/p" "${client_dir}/src/protoprimer/main/protoprimer/primer_kernel.py" )"
echo "INFO: protoprimer_version ${protoprimer_version}" 1>&2

# Determine if it is a dev version (which relaxes many checks):
if [[ "${protoprimer_version}" =~ ^[[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*\.dev.[[:digit:]]*$ ]]
then
    echo "INFO: dev version pattern: ${protoprimer_version}" 1>&2
    is_dev_version="true"
elif [[ "${protoprimer_version}" =~ ^[[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*$ ]]
then
    echo "INFO: release version pattern: ${protoprimer_version}" 1>&2
    is_dev_version="false"
else
    echo "ERROR: unrecognized version pattern: ${protoprimer_version}" 1>&2
    exit 1
fi
echo "INFO: is_dev_version: ${is_dev_version}" 1>&2

# Fetch from upstream:
git_main_remote="origin"
git fetch "${git_main_remote}"

# Check if current commit is in the main branch:
git_main_branch="main"
if ! git merge-base --is-ancestor HEAD "${git_main_remote}/${git_main_branch}"
then
    if [[ "${is_dev_version}" == "true" ]]
    then
        echo "WARN: current HEAD is not in ${git_main_remote}/${git_main_branch}" 1>&2
    else
        echo "ERROR: current HEAD is not in ${git_main_remote}/${git_main_branch}" 1>&2
        exit 1
    fi
else
    echo "INFO: current HEAD is in ${git_main_remote}/${git_main_branch}" 1>&2
fi

git_tag="$(git describe --tags)"
echo "INFO: curr git_tag: ${git_tag}" 1>&2

git_hash="$( git rev-parse HEAD )"
time_stamp="$( date -u +"%Y-%m-%dT%H:%M:%SZ" )"
publisher_user="$( whoami )"
publisher_host="$( hostname )"

# Versions has to be prefixed with `v` in tag:
if [[ "v${protoprimer_version}" != "${git_tag}" ]]
then
    git_tag="v${protoprimer_version}"
    if [[ "${is_dev_version}" != "true" ]]
    then
        # Append `.final` for non-dev (release) version to make a tag:
        git_tag="${git_tag}.final"
    fi
    echo "INFO: next git_tag: ${git_tag}" 1>&2
    # No matching tag exists yet:
    if true
    then
        # Note: unsigned unannotated tags appear "Verified" in GitHub:
        git tag "${git_tag}"
    else
        # Note: unsigned annotated does not appear "Verified" in GitHub:
        git tag --annotate "${git_tag}" -m "${git_hash} | ${time_stamp} | ${publisher_user} | ${publisher_host}"
    fi
else
    # Matching tag already exists - either already released or something is wrong.
    # It can be fixed by removing the tag, but user has to do it consciously.
    echo "ERROR: tag already exits: ${git_tag}" 1>&2
    exit 1
fi

# Push to remote only if it is non-dev version:
if [[ "${is_dev_version}" == "true" ]]
then
    echo "WARN: tag is not pushed to remote: ${git_tag}" 1>&2
else
    echo "INFO: tag is about to be pushed to remote: ${git_tag}" 1>&2
    git push "${git_main_remote}" "${git_tag}"
fi

# Switch to `build_dir`:
build_dir="${client_dir}/src/protoprimer"
cd "${build_dir}"

# Clean up previously built packages:
rm -rf "${build_dir}/dist"

# Create temporary `venv` for twine (do not pollute `venv` used for `protoprimer`):
rm -rf         "${build_dir}/venv.twine"
python -m venv "${build_dir}/venv.twine"
source         "${build_dir}/venv.twine/bin/activate"
pip install setuptools

# The following are the staps found in majority of the web resources.
python "${build_dir}/setup.py" sdist --verbose

pip install twine
# This will prompt for login credentials:
twine upload --verbose "${build_dir}/dist/protoprimer-${protoprimer_version}.tar.gz"

# Switch back to `client_dir`:
cd "${client_dir}"

# Change version to non-release-able to force user to change it later:
sed --in-place \
"s/${protoprimer_version}/WRONG_TO_BE_FIXED.${protoprimer_version}/g" \
"${client_dir}/src/protoprimer/main/protoprimer/primer_kernel.py" \
