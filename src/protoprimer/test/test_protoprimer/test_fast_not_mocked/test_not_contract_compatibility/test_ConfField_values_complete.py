"""
FT_78_72_23_04.backward_compatibility.md
"""

from local_test.case_condition import requires_max_python
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import ConfField
from test_protoprimer.test_fast_not_mocked.test_contract_compatibility.test_ConfField_values import (
    frozen_conf_field_values,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ConfField.__name__,
    )


def test_every_conf_field_is_frozen():
    """
    Not a contract test: the baseline's copy would fail on any new field (additions must not fail the contract).
    """

    # given:
    current_conf_field_values = {conf_field.value for conf_field in ConfField}

    # then:
    assert current_conf_field_values == set(frozen_conf_field_values)


@requires_max_python
def test_every_conf_field_is_known_to_the_schema():
    """
    Not a contract test: the baseline's schema does not know the fields added since.
    """

    # given:
    # `pydantic` requires newer `python` than min: import it only when the test runs.
    from local_config_schema.schema import find_known_field_names

    current_conf_field_values = {conf_field.value for conf_field in ConfField}

    # then:
    assert current_conf_field_values == set(find_known_field_names())
