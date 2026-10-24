"""
Helper for the CLI compatibility check via a `cliff`-based spec.

See: FT_78_72_23_04.backward_compatibility.md
"""

from __future__ import annotations

import argparse
from typing import Dict, List


def find_spec_mismatches(
    expected_spec_values: Dict[str, object],
    actual_args: argparse.Namespace,
) -> List[str]:
    """
    Compare only from the spec to the actual args: every spec value must still be there and equal.

    Extra attributes in `actual_args` are ignored: a new arg/option is backward-compatible.
    """

    spec_mismatches = []
    for spec_name, spec_value in expected_spec_values.items():
        if not hasattr(actual_args, spec_name):
            spec_mismatches.append(f"[{spec_name}] is missing (expected [{spec_value}])")
        elif getattr(actual_args, spec_name) != spec_value:
            spec_mismatches.append(f"[{spec_name}] is [{getattr(actual_args, spec_name)}] (expected [{spec_value}])")
    return spec_mismatches
