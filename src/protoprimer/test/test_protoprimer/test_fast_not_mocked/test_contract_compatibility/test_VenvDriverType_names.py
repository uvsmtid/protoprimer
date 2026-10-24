"""
`VenvDriverType` names are values of the `venv_driver` config field and of `PROTOPRIMER_VENV_DRIVER`: they are frozen.

FT_78_72_23_04.backward_compatibility.md
"""

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import VenvDriverType

# The names are frozen here: they can be added, but must not be removed or renamed:
frozen_venv_driver_type_names = [
    "venv_pip",
    "venv_uv",
]


def test_relationship():
    assert_test_module_name_embeds_str(
        VenvDriverType.__name__,
    )


@pytest.mark.parametrize("frozen_venv_driver_type_name", frozen_venv_driver_type_names)
def test_frozen_venv_driver_type_name_exists(frozen_venv_driver_type_name):

    # given:
    current_venv_driver_type_names = {venv_driver_type.name for venv_driver_type in VenvDriverType}

    # then:
    assert frozen_venv_driver_type_name in current_venv_driver_type_names
