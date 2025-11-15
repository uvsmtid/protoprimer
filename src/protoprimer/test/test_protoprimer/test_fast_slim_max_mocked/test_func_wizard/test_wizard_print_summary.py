import copy
import json
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfLeap,
    wizard_print_summary,
    WizardField,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        wizard_print_summary.__name__,
    )


@pytest.mark.parametrize(
    "conf_leap",
    [conf_leap for conf_leap in ConfLeap],
)
@patch("builtins.print")
def test_wizard_print_summary(
    mock_print,
    conf_leap: ConfLeap,
):

    # given:
    mock_state_node = MagicMock()
    file_data = {}
    for wizard_field in WizardField:
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            file_data,
            f"value_{wizard_meta.field_name}",
        )
    original_file_data = copy.deepcopy(file_data)

    expected_summary_data = {}
    for _, wizard_field in WizardField.enumerate_conf_leap_wizardable_fields(conf_leap):
        wizard_meta = wizard_field.value
        value = wizard_meta.read_value(
            wizard_meta,
            mock_state_node,
            file_data,
        )
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            expected_summary_data,
            value,
        )

    # when:

    wizard_print_summary(
        file_data,
        conf_leap,
    )

    # then:

    mock_print.assert_called_once_with(
        json.dumps(
            expected_summary_data,
            indent=4,
        )
    )
    assert file_data == original_file_data


@pytest.mark.parametrize(
    "conf_leap",
    [
        conf_leap
        for conf_leap in ConfLeap
        if len(list(WizardField.enumerate_conf_leap_wizardable_fields(conf_leap))) > 0
    ],
)
@patch("builtins.print")
def test_wizard_print_summary_missing_field(
    mock_print,
    conf_leap: ConfLeap,
):

    # given:
    mock_state_node = MagicMock()
    file_data = {}
    wizard_fields = list(WizardField.enumerate_conf_leap_wizardable_fields(conf_leap))
    for _, wizard_field in wizard_fields[1:]:
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            file_data,
            f"value_{wizard_meta.field_name}",
        )

    # when:

    with pytest.raises(AssertionError) as exc_info:
        wizard_print_summary(
            file_data,
            conf_leap,
        )

    # then:

    missing_wizard_meta = wizard_fields[0][1].value
    assert str(exc_info.value) == (
        f"missing field_name [{missing_wizard_meta.field_name}] in field_data [{file_data}] with root_ancestor_field [{missing_wizard_meta.root_ancestor_field}]"
    )
    mock_print.assert_not_called()
