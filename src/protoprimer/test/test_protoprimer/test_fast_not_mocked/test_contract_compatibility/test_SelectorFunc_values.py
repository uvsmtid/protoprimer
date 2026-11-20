"""
Selector function names (looked up by name in the client's selector scripts) are frozen: a rename is a break
which no config schema can see (these names are in `python` scripts, not in config files).

FT_78_72_23_04.backward_compatibility.md
"""

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import _SelectorFunc

# The selector function names are frozen here: they can be added, but must not be removed or renamed:
frozen_selector_func_values = [
    "select_python_file_abs_path",
    "select_env_dir_rel_path",
]


def test_relationship():
    assert_test_module_name_embeds_str(
        _SelectorFunc.__name__,
    )


@pytest.mark.parametrize("frozen_selector_func_value", frozen_selector_func_values)
def test_frozen_selector_func_value_exists(frozen_selector_func_value):

    # given:
    current_selector_func_values = {selector_func.value for selector_func in _SelectorFunc}

    # then:
    assert frozen_selector_func_value in current_selector_func_values
