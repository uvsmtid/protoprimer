from unittest.mock import (
    MagicMock,
)

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    WizardField,
    FieldWizardMeta,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        WizardField.read_field_env_build_root_dir_rel_path.__name__,
    )


def test_read_field_env_build_root_dir_rel_path_no_descriptors():
    """
    Tests when `field_env_project_descriptors` is not in `file_data`.
    """

    # given:

    file_data = {}
    mock_state_node = MagicMock()
    wizard_meta = MagicMock(spec=FieldWizardMeta)

    # when:

    result = WizardField.read_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result == "."


def test_read_field_env_build_root_dir_rel_path_empty_descriptors():
    """
    Tests when `field_env_project_descriptors` is an empty list.
    """

    # given:

    file_data = {
        ConfField.field_env_project_descriptors.value: [],
    }

    mock_state_node = MagicMock()
    wizard_meta = MagicMock(spec=FieldWizardMeta)

    # when:

    result = WizardField.read_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result == "."


def test_read_field_env_build_root_dir_rel_path_no_build_root():
    """
    Tests when `field_env_project_descriptors` has one project, but `field_env_build_root_dir_rel_path` is not in it.
    """

    # given:

    file_data = {
        ConfField.field_env_project_descriptors.value: [
            {},
        ],
    }

    mock_state_node = MagicMock()
    wizard_meta = MagicMock(spec=FieldWizardMeta)

    # when:

    result = WizardField.read_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result == "."


def test_read_field_env_build_root_dir_rel_path_with_build_root():
    """
    Tests when `field_env_project_descriptors` has one project, and `field_env_build_root_dir_rel_path` is present.
    """

    # given:

    file_data = {
        ConfField.field_env_project_descriptors.value: [
            {
                ConfField.field_env_build_root_dir_rel_path.value: "some/path",
            },
        ],
    }
    mock_state_node = MagicMock()
    wizard_meta = MagicMock(spec=FieldWizardMeta)

    # when:

    result = WizardField.read_field_env_build_root_dir_rel_path(
        wizard_meta,
        mock_state_node,
        file_data,
    )

    # then:

    assert result == "some/path"
