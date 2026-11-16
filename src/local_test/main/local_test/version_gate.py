import re

import pytest
from packaging.version import Version

import protoprimer


def new_code_version() -> Version:
    """
    The version of the `protoprimer` under test (the imported one, not the one next to the test file).

    FT_60_28_38_74.compatibility_maintenance.md
    """

    # Ignore `.devN` etc. to gate on release boundaries:
    return Version(Version(protoprimer.__version__).base_version)


def since(version_str: str):
    """
    Run the test only for `protoprimer` version `>= version_str`.
    """

    return pytest.mark.skipif(
        new_code_version() < Version(version_str),
        reason=f"applies since `protoprimer` version [{version_str}]",
    )


def until(version_str: str):
    """
    Run the test only for `protoprimer` version `< version_str`.
    """

    return pytest.mark.skipif(
        new_code_version() >= Version(version_str),
        reason=f"applies until `protoprimer` version [{version_str}] (exclusive)",
    )


def proto_kernel_version() -> Version:
    """
    The version of the `proto_kernel.py` which tests use
    (it is the old one in `old_proto_on_new_venv`, see `FT_78_72_23_04.backward_compatibility.md`).
    """

    # Imported here to see the source patched by `old_proto_kernel_in_use`:
    from local_test import integrated_helper

    with open(integrated_helper.get_proto_kernel_source_abs_path()) as proto_kernel_file:
        match = re.search(r'^__version__ = "([^"]+)"', proto_kernel_file.read(), re.MULTILINE)
    assert match is not None
    return Version(Version(match.group(1)).base_version)


def skip_if_proto_kernel_older_than(version_str: str):
    """
    Call at the start of a test of behavior introduced in `version_str`: it is skipped for an older `proto_kernel.py`.
    """

    if proto_kernel_version() < Version(version_str):
        pytest.skip(f"`proto_kernel.py` is older than [{version_str}]: the behavior is not there")
