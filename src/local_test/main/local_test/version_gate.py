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
