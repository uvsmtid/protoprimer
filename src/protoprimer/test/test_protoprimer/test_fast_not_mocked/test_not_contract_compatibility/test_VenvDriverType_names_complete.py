"""
FT_78_72_23_04.backward_compatibility.md
"""

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import VenvDriverType
from test_protoprimer.test_fast_not_mocked.test_contract_compatibility.test_VenvDriverType_names import (
    frozen_venv_driver_type_names,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        VenvDriverType.__name__,
    )


def test_every_venv_driver_type_is_frozen():
    """
    Not a contract test: the baseline's copy would fail on any new driver (additions must not fail the contract).
    """

    # given:
    current_venv_driver_type_names = {venv_driver_type.name for venv_driver_type in VenvDriverType}

    # then:
    assert current_venv_driver_type_names == set(frozen_venv_driver_type_names)
