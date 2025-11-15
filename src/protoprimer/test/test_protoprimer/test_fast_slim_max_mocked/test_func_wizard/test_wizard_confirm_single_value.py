from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfLeap,
    FieldWizardMeta,
    TermColor,
    wizard_confirm_single_value,
)


def write_value_side_effect(
    wizard_meta,
    state_node,
    file_data,
    field_value,
):
    file_data[wizard_meta.field_name] = field_value


def test_relationship():
    assert_test_module_name_embeds_str(
        wizard_confirm_single_value.__name__,
    )


@patch("builtins.input", side_effect=["", "y"])
def test_wizard_confirm_single_value_happy_path_default(mock_input: MagicMock):
    """
    Accepts default value.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_read_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "default_value",
    )
    assert mock_input.call_count == 2
    assert file_data == {
        "test_field": "default_value",
    }


@patch("builtins.input", side_effect=["new_value", "y"])
def test_wizard_confirm_single_value_new_value(mock_input: MagicMock):
    """
    A new value provided by the user.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_read_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "new_value",
    )
    assert mock_input.call_count == 2
    assert file_data == {
        "test_field": "new_value",
    }


@patch("builtins.input", side_effect=["new_value", "n", "another_value", "y"])
def test_wizard_confirm_single_value_retry(mock_input: MagicMock):
    """
    The user rejects the first new value and retries.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    assert mock_read_value.call_count == 2
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "another_value",
    )
    assert mock_input.call_count == 4
    assert file_data == {
        "test_field": "another_value",
    }


@patch("builtins.input", side_effect=["new_value", ""])
def test_wizard_confirm_single_value_skip(mock_input: MagicMock):
    """
    The user skips entering a new value.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_read_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "default_value",
    )
    assert mock_input.call_count == 2
    assert file_data == {"test_field": "default_value"}


@patch("builtins.input", side_effect=["a"])
def test_wizard_confirm_single_value_with_warning(mock_input: MagicMock):
    """
    A warning is shown.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)
    mock_warn = MagicMock(return_value="This is a warning")

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=mock_warn,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )
    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_warn.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_read_value.assert_not_called()
    mock_write_value.assert_not_called()
    mock_input.assert_called_once()
    assert file_data == {}


@patch("builtins.input", side_effect=["", "a"])
def test_wizard_confirm_single_value_with_warning_retry(mock_input: MagicMock):
    """
    A warning is shown, but the user does not acknowledge it right away.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)
    mock_warn = MagicMock(return_value="This is a warning")

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=mock_warn,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )
    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_warn.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_read_value.assert_not_called()
    mock_write_value.assert_not_called()
    assert mock_input.call_count == 2
    assert file_data == {}


@patch("builtins.input", side_effect=["new_value", "invalid", "y"])
def test_wizard_confirm_single_value_invalid_confirmation(mock_input: MagicMock):
    """
    Invalid confirmation input re-prints the confirmation question.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_read_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "new_value",
    )
    assert mock_input.call_count == 3
    assert file_data == {
        "test_field": "new_value",
    }


@patch("builtins.input", side_effect=["invalid_value", "valid_value", "y"])
@patch("builtins.print")
def test_wizard_confirm_single_value_invalid_value(
    mock_print: MagicMock,
    mock_input: MagicMock,
):
    """
    Invalid value re-prompts the user.
    """

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)
    mock_validate_value = MagicMock(
        side_effect=[
            # call 1:
            "Invalid value error",
            # call 2:
            None,
        ]
    )

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=mock_validate_value,
        review_value=lambda wizard_meta, state_node, file_data, field_value: None,
        write_value=mock_write_value,
    )

    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    assert mock_read_value.call_count == 2
    # call 1: invalid attempt:
    mock_read_value.assert_any_call(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    # call 2: valid attempt:
    mock_read_value.assert_any_call(
        wizard_meta,
        mock_state_node,
        file_data,
    )
    assert mock_validate_value.call_count == 2
    mock_validate_value.assert_any_call(
        wizard_meta,
        mock_state_node,
        file_data,
        "invalid_value",
    )
    mock_validate_value.assert_any_call(
        wizard_meta,
        mock_state_node,
        file_data,
        "valid_value",
    )
    mock_write_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "valid_value",
    )
    assert mock_input.call_count == 3
    mock_print.assert_any_call(
        f"{TermColor.error_text.value}Invalid value error{TermColor.reset_style.value}"
    )
    assert file_data == {
        "test_field": "valid_value",
    }


@patch("builtins.input", side_effect=["new_value", "y"])
@patch("builtins.print")
def test_wizard_confirm_single_value_with_review(
    mock_print: MagicMock,
    mock_input: MagicMock,
):

    # given:

    mock_state_node = MagicMock()

    mock_read_value = MagicMock(return_value="default_value")
    mock_write_value = MagicMock(side_effect=write_value_side_effect)
    mock_review_value = MagicMock(return_value="This is a review.")

    wizard_meta = FieldWizardMeta(
        field_name="test_field",
        field_help=lambda wizard_meta, state_node, file_data: "help for test field",
        field_possible_leaps=[ConfLeap.leap_primer],
        field_wizard_leaps=[ConfLeap.leap_primer],
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=mock_read_value,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: None,
        review_value=mock_review_value,
        write_value=mock_write_value,
    )
    file_data = {}

    # when:

    wizard_confirm_single_value(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        wizard_meta=wizard_meta,
        file_data=file_data,
        sub_ordinal_n=1,
        sub_size=1,
        total_ordinal_n=1,
        total_size=1,
    )

    # then:

    mock_review_value.assert_called_once_with(
        wizard_meta,
        mock_state_node,
        file_data,
        "new_value",
    )
    mock_print.assert_any_call(
        f"{TermColor.field_review.value}This is a review.{TermColor.reset_style.value}"
    )
