"""
Every private name that `primer_kernel` fetches by `getattr` from another kernel copy must be listed as required.

Not a contract test: it checks the current source against the list in `test_public_API.py`.

FT_78_72_23_04.backward_compatibility.md
"""

from __future__ import annotations

import ast
import pathlib

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from test_protoprimer.test_fast_not_mocked.test_contract_compatibility.test_public_API import (
    required_obj_paths,
)


def find_getattr_target_names(source: str) -> set[str]:
    """
    Find `X` in `getattr(imported_kernel, X.__name__)`.
    """
    target_names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) == 2 and isinstance(node.args[0], ast.Name) and node.args[0].id == "imported_kernel" and isinstance(node.args[1], ast.Attribute) and node.args[1].attr == "__name__" and isinstance(node.args[1].value, ast.Name):
            target_names.add(node.args[1].value.id)
    return target_names


def test_relationship():
    assert_test_module_name_embeds_str("getattr_targets_required")


def test_finder_finds_targets():
    source = "a = getattr(imported_kernel, _Foo.__name__)\nb = getattr(other, _Bar.__name__)\nc = getattr(imported_kernel, 'x')"
    assert find_getattr_target_names(source) == {"_Foo"}


def test_every_private_getattr_target_is_required():

    # given:

    target_names = find_getattr_target_names(pathlib.Path(primer_kernel.__file__).read_text())
    assert target_names, "no `getattr(imported_kernel, ...)` targets found: the finder is stale"

    # when:

    missing_names = sorted(
        target_name
        for target_name in target_names
        # Public names are checked by `griffe` anyway:
        if target_name.startswith("_") and f"{primer_kernel.__name__}.{target_name}" not in required_obj_paths
    )

    # then:

    assert missing_names == []
