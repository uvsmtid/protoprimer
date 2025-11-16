from unittest.mock import (
    MagicMock,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    ConfLeap,
    FieldWizardMeta,
    WizardField,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path.__name__,
    )


def test_no_project_descriptors():
    """
    Returns None if the ` project_descriptors ` field is missing.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {}

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is None


def test_empty_project_descriptors():
    """
    Returns `None` if `project_descriptors` is an empty list.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {ConfField.field_project_descriptors.value: []}

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is None


def test_multiple_project_descriptors():
    """
    Returns a warning if `project_descriptors` has more than one item.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {ConfField.field_project_descriptors.value: [{}, {}]}

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is not None
    assert "WARNING" in result


def test_single_project_with_install_extras():
    """
    Returns a warning if the single project descriptor has `install_extras`.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: ".",
                ConfField.field_env_install_extras.value: ["extra1"],
            }
        ]
    }

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is not None
    assert "WARNING" in result


def test_single_project_happy_path():
    """
    Returns `None` for a single project descriptor without `install_extras`.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: ".",
                ConfField.field_env_install_extras.value: [],
            }
        ]
    }

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is None


def test_single_project_no_install_extras():
    """
    Returns `None` for a single project descriptor without `install_extras` field.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: ".",
            }
        ]
    }

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is None


def test_single_project_no_build_root():
    """
    Returns `None` for a single project descriptor without `build_root` field.
    """

    # given:

    wizard_meta = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: "dummy help",
        field_possible_leaps=[ConfLeap.leap_env],
        field_wizard_leaps=[ConfLeap.leap_env],
        root_ancestor_field=None,
        warn_if_not_wizard_able=MagicMock(),
        read_value=MagicMock(spec=WizardField.read_value_trivially),
        validate_value=MagicMock(spec=WizardField.validate_value_trivially),
        review_value=MagicMock(spec=WizardField.review_value_trivially),
        write_value=MagicMock(spec=WizardField.write_value_trivially),
    )
    mock_state_node = MagicMock()
    file_data = {
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_env_install_extras.value: [],
            }
        ]
    }

    # when:

    result = WizardField.warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result is None
