"""
FT_78_72_23_04.backward_compatibility.md
"""

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import EnvVar
from test_protoprimer.test_fast_not_mocked.test_contract_compatibility.test_EnvVar_names import (
    frozen_env_var_values,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvVar.__name__,
    )


def test_every_env_var_is_frozen():
    """
    Not a contract test: the baseline's copy would fail on any new env var (additions must not fail the contract).
    """

    # given:
    current_env_var_values = {env_var.value for env_var in EnvVar}

    # then:
    assert current_env_var_values == set(frozen_env_var_values)
