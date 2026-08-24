from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Tuple

from local_doc.common_func import list_doc_files
from metaprimer.script_lib import configure_script
from protoprimer.primer_kernel import EnvState

logger = logging.getLogger(__name__)

RatedDocFile = Tuple[object, str, Path]

rated_doc_dirs: list[str] = [
    "doc/feature_topic",
    "doc/use_case",
]

epoch_start_date = "1970-01-01"

_link_def_re = re.compile(r"^\[([^\]]+)\]:\s+(\S+)")
_doc_id_filename_re = re.compile(r"^[A-Za-z]+(_\d+)+\.[^.]+\.md$")


def rate_doc() -> None:
    """
    Main func to list all docs from `rated_doc_dirs` ordered by either
    their last git-commit date, their `last_verified` front matter field,
    or the number of other rated docs linking to them.
    """

    arg_parser_instance = init_arg_parser()
    parsed_arguments = arg_parser_instance.parse_args()

    derived_data = configure_script(script_basename=os.path.basename(sys.argv[0]))
    ref_root_abs_path: str = derived_data[EnvState.state_ref_root_dir_abs_path_inited.name]

    all_doc_file_paths: list[Path] = []
    for rated_doc_dir in rated_doc_dirs:
        doc_dir_path = Path(ref_root_abs_path) / rated_doc_dir
        if not doc_dir_path.is_dir():
            logger.warning(f"Directory not found at {doc_dir_path}")
            continue
        all_doc_file_paths.extend(list_doc_files(doc_dir_path))

    rate_by_sort_field = sort_methods[parsed_arguments.sort_field]
    rated_doc_files = rate_by_sort_field(all_doc_file_paths)

    rated_doc_files.sort(
        key=lambda rated_doc_file: (rated_doc_file[0], rated_doc_file[2]),
        reverse=parsed_arguments.reverse_sort,
    )

    for _sort_key, display_value, doc_file_path in rated_doc_files:
        print(f"{display_value} {doc_file_path.relative_to(ref_root_abs_path)}")


def init_arg_parser():
    """
    Initializes and configures the argument parser for the script.

    Returns:
        An instance of `argparse.ArgumentParser`.
    """
    arg_parser_instance = argparse.ArgumentParser(
        description="List feature_topic/use_case docs sorted by a date field or by link count.",
    )
    sort_group = arg_parser_instance.add_mutually_exclusive_group()
    sort_group.add_argument(
        "--last_updated",
        "-u",
        dest="sort_field",
        action="store_const",
        const="last_updated",
        help="Sort by the date of the latest git commit which touched the doc.",
    )
    sort_group.add_argument(
        "--last_verified",
        "-v",
        dest="sort_field",
        action="store_const",
        const="last_verified",
        help="Sort by the `last_verified` front matter field (default; treated as epoch start if missing).",
    )
    sort_group.add_argument(
        "--most_linked",
        "-l",
        dest="sort_field",
        action="store_const",
        const="most_linked",
        help="Sort by the number of other rated docs linking to this doc (most-linked first).",
    )
    arg_parser_instance.set_defaults(sort_field="last_verified")
    arg_parser_instance.add_argument(
        "--reverse_sort",
        "-r",
        dest="reverse_sort",
        action="store_true",
        help="Reverse the selected sort order.",
    )
    return arg_parser_instance


def rate_by_last_updated(doc_file_paths: list[Path]) -> list[RatedDocFile]:
    """
    Rates each doc by the date of the latest git commit which touched it.

    Docs with no git history (e.g., not yet committed) are skipped.
    """
    rated_doc_files: list[RatedDocFile] = []
    for doc_file_path in doc_file_paths:
        rated_date = get_last_updated_date(doc_file_path)
        if rated_date is None:
            logger.warning(f"No git history found for {doc_file_path}")
            continue
        rated_doc_files.append((rated_date, rated_date, doc_file_path))
    return rated_doc_files


def rate_by_last_verified(doc_file_paths: list[Path]) -> list[RatedDocFile]:
    """
    Rates each doc by its `last_verified` front matter field (`epoch_start_date` if missing).
    """
    rated_doc_files: list[RatedDocFile] = []
    for doc_file_path in doc_file_paths:
        rated_date = get_last_verified_date(doc_file_path)
        rated_doc_files.append((rated_date, rated_date, doc_file_path))
    return rated_doc_files


def rate_by_most_linked(doc_file_paths: list[Path]) -> list[RatedDocFile]:
    """
    Rates each doc by the number of other docs (from `doc_file_paths`) linking to it,
    highest link count first.
    """
    link_count_by_basename = count_doc_links(doc_file_paths)
    rated_doc_files: list[RatedDocFile] = []
    for doc_file_path in doc_file_paths:
        link_count = link_count_by_basename.get(doc_file_path.name, 0)
        rated_doc_files.append((-link_count, str(link_count), doc_file_path))
    return rated_doc_files


sort_methods: dict[str, Callable[[list[Path]], list[RatedDocFile]]] = {
    "last_updated": rate_by_last_updated,
    "last_verified": rate_by_last_verified,
    "most_linked": rate_by_most_linked,
}


def get_last_updated_date(doc_file_path: Path) -> str | None:
    """
    Finds the date (`YYYY-MM-DD`) of the latest git commit which touched `doc_file_path`.

    Returns:
        The date string, or `None` if the file has no git history (e.g., not yet committed).
    """
    completed_process = subprocess.run(
        [
            "git",
            "log",
            "-1",
            "--format=%cd",
            "--date=format:%Y-%m-%d",
            "--",
            str(doc_file_path),
        ],
        cwd=doc_file_path.parent,
        capture_output=True,
        text=True,
        check=True,
    )

    last_updated_date = completed_process.stdout.strip()
    if not last_updated_date:
        return None
    return last_updated_date


def get_last_verified_date(doc_file_path: Path) -> str:
    """
    Reads the `last_verified` front matter field from `doc_file_path`.

    Returns:
        The field value, or `epoch_start_date` if the field (or the front matter) is missing.
    """
    front_matter = parse_frontmatter(doc_file_path)
    return front_matter.get("last_verified", epoch_start_date)


def count_doc_links(doc_file_paths: list[Path]) -> dict[str, int]:
    """
    Counts markdown link-definitions (`[label]: target`) pointing at each doc,
    across `doc_file_paths`, keyed by the target doc's basename.

    A doc's link-definition to itself is not counted.
    """
    link_count_by_basename: dict[str, int] = {}
    for doc_file_path in doc_file_paths:
        for line in doc_file_path.read_text().splitlines():
            line_match = _link_def_re.match(line.strip())
            if not line_match:
                continue
            target_basename = Path(line_match.group(2)).name
            if not _doc_id_filename_re.match(target_basename):
                continue
            if target_basename == doc_file_path.name:
                continue
            link_count_by_basename[target_basename] = link_count_by_basename.get(target_basename, 0) + 1
    return link_count_by_basename


def parse_frontmatter(doc_file_path: Path) -> dict[str, str]:
    """
    Parses the leading `---`-delimited YAML front matter block of `doc_file_path`.

    Returns:
        A dict of front matter fields, or an empty dict if there is no front matter.
    """
    file_lines = doc_file_path.read_text().splitlines()
    if not file_lines or file_lines[0].strip() != "---":
        return {}
    header_end = next(
        (line_idx for line_idx in range(1, len(file_lines)) if file_lines[line_idx].strip() == "---"),
        None,
    )
    if header_end is None:
        return {}
    header_dict: dict[str, str] = {}
    for header_line in file_lines[1:header_end]:
        if ":" in header_line:
            field_key, _, field_value = header_line.partition(":")
            header_dict[field_key.strip()] = field_value.strip()
    return header_dict


if __name__ == "__main__":
    rate_doc()
