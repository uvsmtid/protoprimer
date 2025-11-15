from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfLeap,
    StateNode,
    wizard_conf_leap,
    wizard_confirm_single_value,
    wizard_print_summary,
    WizardField,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        wizard_conf_leap.__name__,
    )


def confirm_single_value_side_effect(
    state_node,
    conf_leap,
    wizard_meta,
    file_data,
    sub_ordinal_n,
    sub_size,
    total_ordinal_n,
    total_size,
):
    wizard_meta.write_value(
        wizard_meta,
        state_node,
        file_data,
        f"value_{wizard_meta.field_name}",
    )


@pytest.mark.parametrize(
    "conf_leap",
    [conf_leap for conf_leap in ConfLeap],
)
@patch(f"{primer_kernel.__name__}.{wizard_print_summary.__name__}")
@patch(
    f"{primer_kernel.__name__}.{wizard_confirm_single_value.__name__}",
    side_effect=confirm_single_value_side_effect,
)
@patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
@patch("builtins.input", side_effect=["y"])
def test_wizard_conf_leap_happy_path(
    mock_input: MagicMock,
    mock_state_node: MagicMock,
    mock_wizard_confirm_single_value: MagicMock,
    mock_wizard_print_summary: MagicMock,
    conf_leap: ConfLeap,
):
    """
    Accepts all values without retries.
    """

    # given:

    file_data = {}
    conf_abs_path = "/test/path"

    expected_file_data = {}
    for _, wizard_field in WizardField.enumerate_conf_leap_wizardable_fields(conf_leap):
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            expected_file_data,
            f"value_{wizard_meta.field_name}",
        )

    # when:

    wizard_conf_leap(
        mock_state_node,
        conf_leap=conf_leap,
        conf_abs_path=conf_abs_path,
        file_data=file_data,
    )

    # then:

    assert mock_input.call_count == 1
    assert mock_wizard_confirm_single_value.call_count == len(
        WizardField.enumerate_conf_leap_wizardable_fields(conf_leap)
    )
    assert mock_wizard_print_summary.call_count == 2
    assert file_data == expected_file_data


@patch(f"{primer_kernel.__name__}.{wizard_print_summary.__name__}")
@patch(
    f"{primer_kernel.__name__}.{wizard_confirm_single_value.__name__}",
    side_effect=confirm_single_value_side_effect,
)
@patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
@patch("builtins.input", side_effect=["n", "y"])
def test_wizard_conf_leap_retry(
    mock_input: MagicMock,
    mock_state_node: MagicMock,
    mock_wizard_confirm_single_value: MagicMock,
    mock_wizard_print_summary: MagicMock,
):
    """
    The user rejects the first summary and retries.
    """

    # given:

    file_data = {}
    conf_leap = ConfLeap.leap_primer
    conf_abs_path = "/test/path"

    expected_file_data = {}
    for _, wizard_field in WizardField.enumerate_conf_leap_wizardable_fields(conf_leap):
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            expected_file_data,
            f"value_{wizard_meta.field_name}",
        )

    # when:

    wizard_conf_leap(
        mock_state_node,
        conf_leap=conf_leap,
        conf_abs_path=conf_abs_path,
        file_data=file_data,
    )

    # then:

    assert mock_input.call_count == 2
    assert mock_wizard_confirm_single_value.call_count == 2 * len(
        WizardField.enumerate_conf_leap_wizardable_fields(conf_leap)
    )
    assert mock_wizard_print_summary.call_count == 4
    assert file_data == expected_file_data


@patch(f"{primer_kernel.__name__}.{wizard_print_summary.__name__}")
@patch(
    f"{primer_kernel.__name__}.{wizard_confirm_single_value.__name__}",
    side_effect=confirm_single_value_side_effect,
)
@patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
@patch("builtins.input", side_effect=["", "y"])
def test_wizard_conf_leap_blank_confirmation(
    mock_input: MagicMock,
    mock_state_node: MagicMock,
    mock_wizard_confirm_single_value: MagicMock,
    mock_wizard_print_summary: MagicMock,
):
    """
    The user provides blank input for confirmation, and the prompt is reprinted.
    """

    # given:

    file_data = {}
    conf_leap = ConfLeap.leap_primer
    conf_abs_path = "/test/path"

    expected_file_data = {}
    for _, wizard_field in WizardField.enumerate_conf_leap_wizardable_fields(conf_leap):
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            expected_file_data,
            f"value_{wizard_meta.field_name}",
        )

    # when:

    wizard_conf_leap(
        mock_state_node,
        conf_leap=conf_leap,
        conf_abs_path=conf_abs_path,
        file_data=file_data,
    )

    # then:

    assert mock_input.call_count == 2
    assert mock_wizard_confirm_single_value.call_count == len(
        WizardField.enumerate_conf_leap_wizardable_fields(conf_leap)
    )
    assert mock_wizard_print_summary.call_count == 2
    assert file_data == expected_file_data


@patch(f"{primer_kernel.__name__}.{wizard_print_summary.__name__}")
@patch(
    f"{primer_kernel.__name__}.{wizard_confirm_single_value.__name__}",
    side_effect=confirm_single_value_side_effect,
)
@patch(f"{primer_kernel.__name__}.{StateNode.__name__}")
@patch("builtins.input", side_effect=["invalid", "y"])
def test_wizard_conf_leap_invalid_confirmation(
    mock_input: MagicMock,
    mock_state_node: MagicMock,
    mock_wizard_confirm_single_value: MagicMock,
    mock_wizard_print_summary: MagicMock,
):
    """
    The user provides invalid input for confirmation, and the prompt is reprinted.
    """

    # given:

    file_data = {}
    conf_leap = ConfLeap.leap_primer
    conf_abs_path = "/test/path"

    expected_file_data = {}
    for _, wizard_field in WizardField.enumerate_conf_leap_wizardable_fields(conf_leap):
        wizard_meta = wizard_field.value
        wizard_meta.write_value(
            wizard_meta,
            mock_state_node,
            expected_file_data,
            f"value_{wizard_meta.field_name}",
        )

    # when:

    wizard_conf_leap(
        mock_state_node,
        conf_leap=conf_leap,
        conf_abs_path=conf_abs_path,
        file_data=file_data,
    )

    # then:

    assert mock_input.call_count == 2
    assert mock_wizard_confirm_single_value.call_count == len(
        WizardField.enumerate_conf_leap_wizardable_fields(conf_leap)
    )
    assert mock_wizard_print_summary.call_count == 2
    assert file_data == expected_file_data
