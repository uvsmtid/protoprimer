"""
Guard: the swap is implicit (an autouse fixture in `conftest.py`), so make sure it really happens:
otherwise every test in this dir would pass vacuously with the current `_generate_entry_script_content`.

FT_78_72_23_04.backward_compatibility.md
"""

import functools

# The fixture replaces this name in the module of the test which uses it:
from protoprimer.primer_kernel import _generate_entry_script_content

from local_contract_compatibility.old_entry_on_new_proto import generate_entry_script_content_via_old_wrap


def test_generate_entry_script_content_is_the_old_wrap_adapter():
    assert isinstance(_generate_entry_script_content, functools.partial)
    assert _generate_entry_script_content.func is generate_entry_script_content_via_old_wrap
