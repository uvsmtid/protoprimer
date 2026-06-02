from __future__ import annotations

from pathlib import Path

import pytest

from local_doc.common_func import list_doc_files
from local_test.repo_tree import change_to_known_repo_path
from test_local_doc.doc_verifier import (
    assert_doc_id_link_captions_are_slug,
    assert_doc_id_link_labels_match_basename,
    assert_h1_title_matches_filename,
    assert_has_yaml_header,
    assert_id_matches_filename,
    assert_status_valid,
    assert_title_slug_matches_filename,
    assert_title_tokens_in_title,
)

with change_to_known_repo_path():
    _uc_files = list_doc_files(Path("doc/use_case").resolve())

_valid_case_statuses = {"TODO", "TEST", "DONE"}


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_has_yaml_header(file_path: Path) -> None:
    assert_has_yaml_header(file_path)


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_use_case_id_matches_filename(file_path: Path) -> None:
    assert_id_matches_filename(file_path, "use_case")


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_case_status_valid(file_path: Path) -> None:
    assert_status_valid(file_path, "case_status", _valid_case_statuses)


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_case_title_tokens_in_title(file_path: Path) -> None:
    assert_title_tokens_in_title(file_path, "case_title")


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_case_title_slug_matches_filename(file_path: Path) -> None:
    assert_title_slug_matches_filename(file_path, "case_title")


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_h1_title_matches_filename(file_path: Path) -> None:
    assert_h1_title_matches_filename(file_path)


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_doc_id_link_labels_match_basename(file_path: Path) -> None:
    assert_doc_id_link_labels_match_basename(file_path)


@pytest.mark.parametrize(
    "file_path",
    _uc_files,
    ids=[doc_file.name for doc_file in _uc_files],
)
def test_doc_id_link_captions_are_slug(file_path: Path) -> None:
    assert_doc_id_link_captions_are_slug(file_path)
