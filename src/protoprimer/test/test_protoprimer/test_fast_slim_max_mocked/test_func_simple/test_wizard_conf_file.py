from unittest.mock import (
    MagicMock,
    patch,
)

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    wizard_conf_file,
    ConfLeap,
    WizardStage,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        wizard_conf_file.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.write_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.makedirs")
@patch(f"{protoprimer.primer_kernel.__name__}.wizard_conf_leap")
@patch(f"{protoprimer.primer_kernel.__name__}.verify_conf_file_data")
@patch(f"{protoprimer.primer_kernel.__name__}.read_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.path.exists")
def test_wizard_conf_file_existing_file(
    mock_os_path_exists,
    mock_read_json_file,
    mock_verify_conf_file_data,
    mock_wizard_conf_leap,
    mock_os_makedirs,
    mock_write_json_file,
):
    # given:
    mock_os_path_exists.return_value = True
    mock_read_json_file.return_value = {"existing_key": "existing_value"}

    mock_state_node = MagicMock()
    mock_state_node.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value.return_value = (
        WizardStage.wizard_started
    )

    conf_abs_path_dummy = "/dummy/path/to/conf.json"
    default_file_data_dummy = {"default_key": "default_value"}

    # when:
    returned_file_data = wizard_conf_file(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        conf_abs_path=conf_abs_path_dummy,
        default_file_data=default_file_data_dummy,
    )

    # then:
    mock_os_path_exists.assert_called_once_with(conf_abs_path_dummy)
    mock_read_json_file.assert_called_once_with(conf_abs_path_dummy)
    mock_verify_conf_file_data.assert_called_once_with(
        conf_abs_path_dummy,
        {"existing_key": "existing_value"},
        ConfLeap.leap_primer,
    )
    mock_wizard_conf_leap.assert_called_once_with(
        mock_state_node,
        ConfLeap.leap_primer,
        conf_abs_path_dummy,
        {"existing_key": "existing_value"},
    )
    mock_os_makedirs.assert_called_once_with("/dummy/path/to", exist_ok=True)
    mock_write_json_file.assert_called_once_with(
        conf_abs_path_dummy,
        {"existing_key": "existing_value"},
    )
    assert returned_file_data == {"existing_key": "existing_value"}


@patch(f"{protoprimer.primer_kernel.__name__}.write_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.makedirs")
@patch(f"{protoprimer.primer_kernel.__name__}.wizard_conf_leap")
@patch(f"{protoprimer.primer_kernel.__name__}.verify_conf_file_data")
@patch(f"{protoprimer.primer_kernel.__name__}.read_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.path.exists")
def test_wizard_conf_file_non_existing_file(
    mock_os_path_exists,
    mock_read_json_file,
    mock_verify_conf_file_data,
    mock_wizard_conf_leap,
    mock_os_makedirs,
    mock_write_json_file,
):
    # given:
    mock_os_path_exists.return_value = False

    mock_state_node = MagicMock()
    mock_state_node.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value.return_value = (
        WizardStage.wizard_started
    )

    conf_abs_path_dummy = "/dummy/path/to/conf.json"
    default_file_data_dummy = {"default_key": "default_value"}

    # when:
    returned_file_data = wizard_conf_file(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        conf_abs_path=conf_abs_path_dummy,
        default_file_data=default_file_data_dummy,
    )

    # then:
    mock_os_path_exists.assert_called_once_with(conf_abs_path_dummy)
    mock_read_json_file.assert_not_called()
    mock_verify_conf_file_data.assert_called_once_with(
        conf_abs_path_dummy,
        default_file_data_dummy,
        ConfLeap.leap_primer,
    )
    mock_wizard_conf_leap.assert_called_once_with(
        mock_state_node,
        ConfLeap.leap_primer,
        conf_abs_path_dummy,
        default_file_data_dummy,
    )
    mock_os_makedirs.assert_called_once_with("/dummy/path/to", exist_ok=True)
    mock_write_json_file.assert_called_once_with(
        conf_abs_path_dummy,
        default_file_data_dummy,
    )
    assert returned_file_data == default_file_data_dummy


@patch(f"{protoprimer.primer_kernel.__name__}.write_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.makedirs")
@patch(f"{protoprimer.primer_kernel.__name__}.wizard_conf_leap")
@patch(f"{protoprimer.primer_kernel.__name__}.verify_conf_file_data")
@patch(f"{protoprimer.primer_kernel.__name__}.read_json_file")
@patch(f"{protoprimer.primer_kernel.__name__}.os.path.exists")
def test_wizard_conf_file_wizard_finished(
    mock_os_path_exists,
    mock_read_json_file,
    mock_verify_conf_file_data,
    mock_wizard_conf_leap,
    mock_os_makedirs,
    mock_write_json_file,
):
    # given:
    mock_os_path_exists.return_value = True
    mock_read_json_file.return_value = {"existing_key": "existing_value"}

    mock_state_node = MagicMock()
    mock_state_node.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value.return_value = (
        WizardStage.wizard_finished
    )

    conf_abs_path_dummy = "/dummy/path/to/conf.json"
    default_file_data_dummy = {"default_key": "default_value"}

    # when:
    returned_file_data = wizard_conf_file(
        state_node=mock_state_node,
        conf_leap=ConfLeap.leap_primer,
        conf_abs_path=conf_abs_path_dummy,
        default_file_data=default_file_data_dummy,
    )

    # then:
    mock_os_path_exists.assert_called_once_with(conf_abs_path_dummy)
    mock_read_json_file.assert_called_once_with(conf_abs_path_dummy)
    mock_verify_conf_file_data.assert_called_once_with(
        conf_abs_path_dummy,
        {"existing_key": "existing_value"},
        ConfLeap.leap_primer,
    )
    mock_wizard_conf_leap.assert_not_called()
    mock_os_makedirs.assert_not_called()
    mock_write_json_file.assert_not_called()
    assert returned_file_data == {"existing_key": "existing_value"}
