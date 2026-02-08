from unittest.mock import (
    MagicMock,
    patch,
)

from local_doc import cmd_gen_next_doc_id


def test_get_prefix_and_ids_happy_path() -> None:
    # given:
    file_names_list: list[str] = [
        "PR_01_02.md",
        "PR_03_04.txt",
        "PR_05_06.rst",
    ]

    # when:
    doc_prefix, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # then:
    assert doc_prefix == "PR"
    assert existing_ids == {("01", "02"), ("03", "04"), ("05", "06")}
    assert num_id_parts == 2


@patch(f"{cmd_gen_next_doc_id.__name__}.logger")
def test_get_prefix_and_ids_mixed_prefixes(mock_logger: MagicMock) -> None:
    # given:
    file_names_list: list[str] = [
        "PR_01_02.md",
        "OTHER_03_04.txt",
        "PR_05_06.rst",
    ]

    # when:
    doc_prefix, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # then:
    assert doc_prefix == "PR"
    assert existing_ids == {("01", "02"), ("05", "06")}
    assert num_id_parts == 2
    mock_logger.warning.assert_called()


@patch(f"{cmd_gen_next_doc_id.__name__}.logger")
def test_get_prefix_and_ids_inconsistent_id_lengths(mock_logger: MagicMock) -> None:
    # given:
    file_names_list: list[str] = [
        "PR_01_02.md",
        "PR_03_04_05.txt",
        "PR_06_07.rst",
    ]

    # when:
    doc_prefix, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # then:
    assert doc_prefix == "PR"
    assert existing_ids == {("01", "02"), ("06", "07")}
    assert num_id_parts == 2
    mock_logger.warning.assert_called()


def test_get_prefix_and_ids_no_valid_files() -> None:
    # given:
    file_names_list: list[str] = [
        "first.md",
        "second.txt",
        "third",
    ]

    # when:
    doc_prefix, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # then:
    assert doc_prefix is None
    assert existing_ids == set()
    assert num_id_parts == 0


def test_get_prefix_and_ids_empty_list() -> None:
    # given:
    file_names_list: list[str] = []

    # when:
    doc_prefix, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # then:
    assert doc_prefix is None
    assert existing_ids == set()
    assert num_id_parts == 0


@patch(f"{cmd_gen_next_doc_id.__name__}.random.randint")
def test_generate_next_id_empty(mock_randint: MagicMock) -> None:
    # given:
    mock_randint.side_effect = [1, 2, 3, 4]

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(set(), 2)

    # then:
    assert result_tuple == ("01", "02")


@patch(f"{cmd_gen_next_doc_id.__name__}.random.choice")
def test_generate_next_id_digit_by_digit(mock_choice: MagicMock) -> None:
    # given:
    # freqs for 1st digit: 0:1, 1:1. others: 0. min_freq=0.
    # freqs for 2nd digit (if 1st is 0): 0:1. others: 0. min_freq=0.
    existing_ids: set[tuple[str, ...]] = {("00", "00"), ("10", "00")}

    # Let's say random.choice picks '2' for the first digit (from '2'...'9')
    # Then candidates are empty.
    # Then it picks '3' for the second digit.
    # And so on.
    mock_choice.side_effect = ["2", "3", "4", "5"]

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, 2)

    # then:
    assert result_tuple == ("23", "45")
    assert mock_choice.call_count == 4

    # Check the arguments passed to mock_choice. The first call should be with a list of digits.
    # We are trying to verify that '2' is among the choices for the first digit.
    # The actual list passed to random.choice would be least_frequent_digits, which should contain '2'.
    assert "0" not in mock_choice.call_args_list[0][0][0]
    assert "1" not in mock_choice.call_args_list[0][0][0]
    assert "2" in mock_choice.call_args_list[0][0][0]
    assert len(mock_choice.call_args_list[0][0][0]) == 8


@patch(f"{cmd_gen_next_doc_id.__name__}.random.choice")
def test_generate_next_id_user_scenario(mock_choice: MagicMock) -> None:
    # given:
    file_names_list: list[str] = [
        "FT_00_22_19_59.derived_config.md",
        "FT_02_89_37_65.shebang_line.md",
        "FT_08_92_69_92.env_var.md",
        "FT_11_27_29_83.run_mode.md",
        "FT_14_52_73_23.primer_runtime.md",
        "FT_22_11_94_65.bootstrap_precondition.md",
        "FT_23_37_64_44.conf_dst.md",
        "FT_30_24_95_65.state_idempotency.md",
        "FT_36_27_04_22.use_cases.md",
        "FT_44_72_60_67.python_vs_shell.md",
        "FT_46_37_27_11.editable_install.md",
        "FT_57_87_94_94.bootstrap_process.md",
        "FT_59_95_81_63.env_layout.md",
        "FT_62_88_55_10.CLI_compatibility.md",
        "FT_63_61_24_94.protoprimer_dictionary.md",
        "FT_68_54_41_96.state_dependency.md",
        "FT_72_45_12_06.python_executable.md",
        "FT_74_10_40_33.DAG_extension.md",
        "FT_75_87_82_46.entry_script.md",
        "FT_84_11_73_28.supported_python_versions.md",
        "FT_89_41_35_82.conf_leap.md",
        "FT_90_65_67_62.proto_code.md",
        "FT_93_57_03_75.app_vs_lib.md",
        "FT_99_89_51_06.venv_shell.md",
    ]
    _, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )

    # Let's say it picks '5' for the first digit.
    # Then for the second digit, it looks at IDs starting with 5: "57...", "59...".
    # Freqs for 2nd digit: '7':1, '9':1. Others: 0.
    # Let's say it picks '0'.
    # Then candidates are empty.
    # Let's say it picks '1','2','3','4','5','6' for the rest.
    mock_choice.side_effect = ["5", "0", "1", "2", "3", "4", "5", "6"]

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, num_id_parts)

    # then:
    assert result_tuple == ("50", "12", "34", "56")

    # min freq for 1st digit is 2, for digits '1', '2', '4', '5', '8'
    assert sorted(mock_choice.call_args_list[0][0][0]) == ["1", "2", "3", "4", "5", "8"]


def test_generate_random_id_zero_parts() -> None:
    # when:
    result_tuple = cmd_gen_next_doc_id._generate_random_id(0)

    # then:
    assert result_tuple == tuple()


@patch(f"{cmd_gen_next_doc_id.__name__}.os")
@patch(f"{cmd_gen_next_doc_id.__name__}.argparse")
@patch(f"{cmd_gen_next_doc_id.__name__}.random.choice")
@patch(f"{cmd_gen_next_doc_id.__name__}.random.randint")
def test_main_success(
    mock_randint: MagicMock,
    mock_choice: MagicMock,
    mock_argparse: MagicMock,
    mock_os: MagicMock,
    capsys,
) -> None:
    # given:
    mock_choice.side_effect = ["0", "0", "0", "1"]  # 4 digits for 2 parts
    mock_os.path.isdir.return_value = True
    mock_os.listdir.return_value = [
        "PR_01_02.md",
        "PR_03_04.txt",
    ]
    mock_os.path.isfile.return_value = True
    mock_argparse.ArgumentParser.return_value.parse_args.return_value = MagicMock(
        doc_dir="dummy_dir"
    )

    # when:
    cmd_gen_next_doc_id.gen_next_doc_id()

    # then:
    captured_io = capsys.readouterr()
    output_str = captured_io.out.strip()
    assert output_str == "PR_00_01"


@patch(f"{cmd_gen_next_doc_id.__name__}.os")
@patch(f"{cmd_gen_next_doc_id.__name__}.argparse")
@patch(f"{cmd_gen_next_doc_id.__name__}.logger")
def test_main_dir_not_found(
    mock_logger: MagicMock, mock_argparse: MagicMock, mock_os: MagicMock
) -> None:
    # given:
    mock_os.path.isdir.return_value = False
    mock_argparse.ArgumentParser.return_value.parse_args.return_value = MagicMock(
        doc_dir="non_existent_dir"
    )

    # when:
    cmd_gen_next_doc_id.gen_next_doc_id()

    # then:
    mock_logger.error.assert_called_with("Directory not found at non_existent_dir")
