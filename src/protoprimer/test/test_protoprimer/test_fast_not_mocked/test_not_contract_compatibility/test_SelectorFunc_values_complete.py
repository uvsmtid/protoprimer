"""
FT_78_72_23_04.backward_compatibility.md
"""

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import _SelectorFunc
from test_protoprimer.test_fast_not_mocked.test_contract_compatibility.test_SelectorFunc_values import (
    frozen_selector_func_values,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _SelectorFunc.__name__,
    )


def test_every_selector_func_is_frozen():
    """
    Not a contract test: the baseline's copy would fail on any new selector function (additions must not fail the contract).
    """

    # given:
    current_selector_func_values = {selector_func.value for selector_func in _SelectorFunc}

    # then:
    assert current_selector_func_values == set(frozen_selector_func_values)
