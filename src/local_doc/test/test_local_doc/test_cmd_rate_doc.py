from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from local_doc import cmd_rate_doc

_ref_root_abs_path = "/fake_repo"

_ft_dir = f"{_ref_root_abs_path}/doc/feature_topic"
_uc_dir = f"{_ref_root_abs_path}/doc/use_case"


def _create_doc_files(fs) -> None:
    fs.create_dir(_ft_dir)
    fs.create_dir(_uc_dir)

    fs.create_file(
        f"{_ft_dir}/FT_11_11_11_11.aaa.md",
        contents=(
            #
            "---\n"
            "feature_topic: FT_11_11_11_11\n"
            "topic_title: aaa\n"
            "topic_status: DONE\n"
            "last_verified: 2024-03-01\n"
            "---\n"
            "\n"
            # Links to itself (not counted), `bbb` and `ccc`:
            "[FT_11_11_11_11.aaa.md]: FT_11_11_11_11.aaa.md\n"
            "[FT_22_22_22_22.bbb.md]: FT_22_22_22_22.bbb.md\n"
            "[UC_33_33_33_33.ccc.md]: ../use_case/UC_33_33_33_33.ccc.md\n"
        ),
    )
    # No `last_verified` field - should fall back to `epoch_start_date`:
    fs.create_file(
        f"{_ft_dir}/FT_22_22_22_22.bbb.md",
        contents=(
            #
            "---\n"
            "feature_topic: FT_22_22_22_22\n"
            "topic_title: bbb\n"
            "topic_status: TODO\n"
            "---\n"
            "\n"
            # Links to itself (not counted) and `ccc`:
            "[FT_22_22_22_22.bbb.md]: FT_22_22_22_22.bbb.md\n"
            "[UC_33_33_33_33.ccc.md]: ../use_case/UC_33_33_33_33.ccc.md\n"
        ),
    )
    fs.create_file(
        f"{_uc_dir}/UC_33_33_33_33.ccc.md",
        contents=(
            #
            "---\n"
            "use_case: UC_33_33_33_33\n"
            "topic_title: ccc\n"
            "topic_status: DONE\n"
            "last_verified: 2023-01-01\n"
            "---\n"
            "\n"
            # Links only to itself (not counted) - no other doc links here:
            "[UC_33_33_33_33.ccc.md]: UC_33_33_33_33.ccc.md\n"
        ),
    )


@patch(f"{cmd_rate_doc.__name__}.configure_script")
def test_rate_doc_last_verified(mock_configure_script, fs, capsys) -> None:
    # given:
    _create_doc_files(fs)
    mock_configure_script.return_value = {
        cmd_rate_doc.EnvState.state_ref_root_dir_abs_path_inited.name: _ref_root_abs_path,
    }

    # when:
    with patch("sys.argv", ["rate_doc", "--last_verified"]):
        cmd_rate_doc.rate_doc()

    # then:
    output_lines = capsys.readouterr().out.strip().splitlines()
    assert output_lines == [
        f"{cmd_rate_doc.epoch_start_date} doc/feature_topic/FT_22_22_22_22.bbb.md",
        "2023-01-01 doc/use_case/UC_33_33_33_33.ccc.md",
        "2024-03-01 doc/feature_topic/FT_11_11_11_11.aaa.md",
    ]


@patch(f"{cmd_rate_doc.__name__}.get_last_updated_date")
@patch(f"{cmd_rate_doc.__name__}.configure_script")
def test_rate_doc_last_updated(mock_configure_script, mock_get_last_updated_date, fs, capsys) -> None:
    # given:
    _create_doc_files(fs)
    mock_configure_script.return_value = {
        cmd_rate_doc.EnvState.state_ref_root_dir_abs_path_inited.name: _ref_root_abs_path,
    }

    last_updated_by_basename = {
        "FT_11_11_11_11.aaa.md": "2026-01-01",
        "FT_22_22_22_22.bbb.md": "2020-05-05",
        "UC_33_33_33_33.ccc.md": "2023-07-07",
    }
    mock_get_last_updated_date.side_effect = lambda doc_file_path: last_updated_by_basename[doc_file_path.name]

    # when:
    with patch("sys.argv", ["rate_doc", "--last_updated"]):
        cmd_rate_doc.rate_doc()

    # then:
    output_lines = capsys.readouterr().out.strip().splitlines()
    assert output_lines == [
        "2020-05-05 doc/feature_topic/FT_22_22_22_22.bbb.md",
        "2023-07-07 doc/use_case/UC_33_33_33_33.ccc.md",
        "2026-01-01 doc/feature_topic/FT_11_11_11_11.aaa.md",
    ]


@patch(f"{cmd_rate_doc.__name__}.configure_script")
def test_rate_doc_most_linked(mock_configure_script, fs, capsys) -> None:
    # given:
    _create_doc_files(fs)
    mock_configure_script.return_value = {
        cmd_rate_doc.EnvState.state_ref_root_dir_abs_path_inited.name: _ref_root_abs_path,
    }

    # when:
    with patch("sys.argv", ["rate_doc", "--most_linked"]):
        cmd_rate_doc.rate_doc()

    # then:
    # `ccc` is linked from `aaa` and `bbb` (2), `bbb` is linked from `aaa` (1),
    # `aaa` is not linked from any other doc (0). Self-links are not counted.
    # Most-linked is on top by default:
    output_lines = capsys.readouterr().out.strip().splitlines()
    assert output_lines == [
        "2 doc/use_case/UC_33_33_33_33.ccc.md",
        "1 doc/feature_topic/FT_22_22_22_22.bbb.md",
        "0 doc/feature_topic/FT_11_11_11_11.aaa.md",
    ]


@patch(f"{cmd_rate_doc.__name__}.configure_script")
def test_rate_doc_most_linked_reverse_sort(mock_configure_script, fs, capsys) -> None:
    # given:
    _create_doc_files(fs)
    mock_configure_script.return_value = {
        cmd_rate_doc.EnvState.state_ref_root_dir_abs_path_inited.name: _ref_root_abs_path,
    }

    # when:
    with patch("sys.argv", ["rate_doc", "--most_linked", "--reverse_sort"]):
        cmd_rate_doc.rate_doc()

    # then:
    output_lines = capsys.readouterr().out.strip().splitlines()
    assert output_lines == [
        "0 doc/feature_topic/FT_11_11_11_11.aaa.md",
        "1 doc/feature_topic/FT_22_22_22_22.bbb.md",
        "2 doc/use_case/UC_33_33_33_33.ccc.md",
    ]


def test_count_doc_links_excludes_self_links(fs) -> None:
    # given:
    _create_doc_files(fs)
    doc_file_paths = [
        Path(f"{_ft_dir}/FT_11_11_11_11.aaa.md"),
        Path(f"{_ft_dir}/FT_22_22_22_22.bbb.md"),
        Path(f"{_uc_dir}/UC_33_33_33_33.ccc.md"),
    ]

    # when:
    link_count_by_basename = cmd_rate_doc.count_doc_links(doc_file_paths)

    # then:
    assert link_count_by_basename == {
        "FT_22_22_22_22.bbb.md": 1,
        "UC_33_33_33_33.ccc.md": 2,
    }
