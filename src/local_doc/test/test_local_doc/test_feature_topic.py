from __future__ import annotations

from pathlib import Path

import pytest

from local_doc.common_func import list_doc_files
from local_test.repo_tree import change_to_known_repo_path
from test_local_doc.doc_verifier import (
    assert_h1_title_matches_filename,
    assert_has_yaml_header,
    assert_id_matches_filename,
    assert_status_valid,
    assert_title_tokens_in_title,
)

with change_to_known_repo_path():
    _ft_files = list_doc_files(Path("doc/feature_topic").resolve())

_valid_topic_statuses = {"TODO", "TEST", "DONE"}


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_has_yaml_header(file_path: Path) -> None:
    assert_has_yaml_header(file_path)


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_feature_topic_id_matches_filename(file_path: Path) -> None:
    assert_id_matches_filename(file_path, "feature_topic")


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_topic_status_valid(file_path: Path) -> None:
    assert_status_valid(file_path, "topic_status", _valid_topic_statuses)


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_topic_title_tokens_in_title(file_path: Path) -> None:
    assert_title_tokens_in_title(file_path, "topic_title")


@pytest.mark.parametrize(
    "file_path",
    _ft_files,
    ids=[doc_file.name for doc_file in _ft_files],
)
def test_h1_title_matches_filename(file_path: Path) -> None:
    assert_h1_title_matches_filename(file_path)
