"""
The public API of the tree this test belongs to must not be broken by the current `protoprimer`.

Under `old_tests_on_new_changes` this test comes from the baseline worktree,
so the baseline's own tree is compared against the installed (current) `protoprimer`.

FT_78_72_23_04.backward_compatibility.md
"""

import importlib.util
import pathlib

from local_test.case_condition import requires_max_python
from local_test.griffe_helper import find_breaking_api_changes
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _ContextBuilder,
    _EntryFunc,
    _EnvContext,
    _generate_entry_script_content,
    _run_process,
)


# Private (underscore) objects checked as public: "Required API" in FT_78_72_23_04.backward_compatibility.md
required_obj_paths = [
    f"protoprimer.primer_kernel.{_ContextBuilder.__name__}",
    f"protoprimer.primer_kernel.{_EntryFunc.__name__}",
    f"protoprimer.primer_kernel.{_EnvContext.__name__}",
    f"protoprimer.primer_kernel.{_generate_entry_script_content.__name__}",
    f"protoprimer.primer_kernel.{_run_process.__name__}",
    # A variable (no `__name__`): set via `setattr(imported_kernel, ...)` across kernel copies:
    "protoprimer.primer_kernel._proto_kernel_abs_path",
]


def test_relationship():
    assert_test_module_name_embeds_str("public_API")


@requires_max_python
def test_public_api_is_not_broken():

    # given:

    # <project dir>/test/test_protoprimer/<perimeter dir>/<this dir>/<this file>:
    own_main_dir_abs_path = pathlib.Path(__file__).resolve().parents[4] / "main"
    installed_package_dir_abs_path = pathlib.Path(importlib.util.find_spec("protoprimer").submodule_search_locations[0])

    # when:

    breaking_changes = find_breaking_api_changes(
        "protoprimer",
        own_main_dir_abs_path,
        installed_package_dir_abs_path.parent,
        required_obj_paths,
    )

    # then:

    assert breaking_changes == []
