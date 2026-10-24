"""
Helper for the API compatibility check via `griffe`.

See: FT_78_72_23_04.backward_compatibility.md
"""

from __future__ import annotations

import pathlib
from typing import List


def find_breaking_api_changes(
    package_name: str,
    old_search_path: pathlib.Path,
    new_search_path: pathlib.Path,
) -> List[str]:
    """
    Load `package_name` statically (nothing is imported) from two trees and return
    the breaking changes of the public API of `old_search_path` relative to `new_search_path`.

    Additions are not breaking: only removed or changed public names are reported.
    """

    # `griffe` requires newer `python` than min: import it only when the check runs.
    import griffe

    old_package = griffe.load(
        package_name,
        search_paths=[str(old_search_path)],
        allow_inspection=False,
    )
    new_package = griffe.load(
        package_name,
        search_paths=[str(new_search_path)],
        allow_inspection=False,
    )
    return [f"{breakage.obj.path}: {breakage.kind.value}" for breakage in griffe.find_breaking_changes(old_package, new_package)]
