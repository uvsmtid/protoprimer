import pytest
from unittest.mock import MagicMock, patch
from local_repo import cmd_gen_next_doc_id
import os
import argparse
import logging
import random


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


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_generate_next_id_empty(mock_random: MagicMock) -> None:
    # given:
    mock_random.randint.side_effect = [0, 0, 0, 0]

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(set(), 2)

    # then:
    assert result_tuple == ("00", "00")


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_generate_next_id_simple(mock_random: MagicMock) -> None:
    # given:
    mock_random.choice.return_value = "2"
    mock_random.randint.side_effect = [0, 5, 6]
    existing_ids: set[tuple[str, ...]] = {("00", "00"), ("10", "00")}

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, 2)

    # then:
    assert result_tuple == ("20", "56")


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_generate_next_id_chooses_shorter_prefix(mock_random: MagicMock) -> None:
    # given:
    mock_random.choice.return_value = "0"
    mock_random.randint.side_effect = [1, 2, 3]
    existing_ids: set[tuple[str, ...]] = {("80", "00"), ("81", "00")}

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, 2)

    # then:
    assert result_tuple == ("01", "23")


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_generate_next_id_from_prompt(mock_random: MagicMock) -> None:
    # given:
    mock_random.choice.return_value = "9"
    mock_random.randint.side_effect = [0, 1, 2, 3, 4, 5, 6]
    file_names_list: list[str] = [
        "FT_00_00_00_00.file_0.md",
        "FT_10_00_00_00.file_1.md",
        "FT_20_00_00_00.file_2.md",
        "FT_30_00_00_00.file_3.md",
        "FT_40_00_00_00.file_4.md",
        "FT_50_00_00_00.file_5.md",
        "FT_60_00_00_00.file_6.md",
        "FT_70_00_00_00.file_7.md",
        "FT_80_00_00_00.file_8.md",
        "FT_81_00_00_00.file_81.md",
    ]

    # when:
    _, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, num_id_parts)

    # then:
    assert result_tuple == (
        "90",
        "12",
        "34",
        "56",
    )


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_generate_next_id_least_frequent_prefix(mock_random: MagicMock) -> None:
    # given:
    mock_random.choice.return_value = "2"
    # We have 19 files, and each needs 7 random digits for the name, and then the new id needs 7 random digits
    mock_random.randint.side_effect = [random.randint(0, 9) for _ in range(19 * 7 + 7)]

    # Generate a list of prefixes where '2' is the least frequent
    prefix_list = ["0", "1", "3", "4", "5", "6", "7", "8", "9"]
    file_prefixes = []
    for prefix_char in prefix_list:
        file_prefixes.extend([prefix_char] * 2)
    file_prefixes.append("2")

    file_names_list = []
    for index_val, prefix_char in enumerate(file_prefixes):
        random_part = "".join(str(mock_random.randint(0, 9)) for _ in range(7))
        file_names_list.append(f"FT_{prefix_char}{random_part}.file_{index_val}.md")

    # when:
    _, existing_ids, num_id_parts = cmd_gen_next_doc_id.get_prefix_and_ids(
        file_names_list
    )
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, num_id_parts)

    # then:
    assert result_tuple[0].startswith("2")


def test_generate_random_id_zero_parts() -> None:
    # when:
    result_tuple = cmd_gen_next_doc_id._generate_random_id(0)

    # then:
    assert result_tuple == tuple()


@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_construct_id_from_prefix(mock_random: MagicMock) -> None:
    # given:
    mock_random.randint.side_effect = [1, 2, 3, 4]
    id_prefix = "56"
    num_id_parts = 3

    # when:
    result_tuple = cmd_gen_next_doc_id._construct_id_from_prefix(
        id_prefix, num_id_parts
    )

    # then:
    assert result_tuple == (
        "56",
        "12",
        "34",
    )


@patch(f"{cmd_gen_next_doc_id.__name__}._find_best_prefix")
@patch(f"{cmd_gen_next_doc_id.__name__}._generate_random_id")
def test_generate_next_id_fallback(
    mock_gen_random: MagicMock, mock_find_prefix: MagicMock
) -> None:
    # given:
    mock_find_prefix.return_value = None
    mock_gen_random.return_value = ("99", "99")
    existing_ids: set[tuple[str, ...]] = {("00", "00")}
    num_id_parts = 2

    # when:
    result_tuple = cmd_gen_next_doc_id.generate_next_id(existing_ids, num_id_parts)

    # then:
    mock_find_prefix.assert_called_once()
    mock_gen_random.assert_called_once_with(num_id_parts)
    assert result_tuple == ("99", "99")


@patch(f"{cmd_gen_next_doc_id.__name__}.os")
@patch(f"{cmd_gen_next_doc_id.__name__}.argparse")
@patch(f"{cmd_gen_next_doc_id.__name__}.random")
def test_main_success(
    mock_random: MagicMock, mock_argparse: MagicMock, mock_os: MagicMock, capsys
) -> None:
    # given:
    mock_random.choice.return_value = "2"
    mock_random.randint.side_effect = [0, 5, 6]
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
    assert output_str == "PR_20_56"


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
