from __future__ import annotations

import argparse
import logging
import subprocess
from pathlib import Path

from local_doc.common_func import list_doc_files

logger = logging.getLogger(__name__)

rated_doc_dirs: list[str] = [
    "doc/feature_topic",
    "doc/use_case",
]

epoch_start_date = "1970-01-01"


def rate_doc() -> None:
    """
    Main func to list all docs from `rated_doc_dirs` ordered by either
    their last git-commit date or their `last_verified` front matter field.
    """

    arg_parser_instance = init_arg_parser()
    parsed_arguments = arg_parser_instance.parse_args()

    dated_doc_files: list[tuple[str, Path]] = []

    for rated_doc_dir in rated_doc_dirs:
        doc_dir_path = Path(rated_doc_dir).resolve()
        if not doc_dir_path.is_dir():
            logger.warning(f"Directory not found at {doc_dir_path}")
            continue
        for doc_file_path in list_doc_files(doc_dir_path):
            if parsed_arguments.sort_field == "last_updated":
                rated_date = get_last_updated_date(doc_file_path)
                if rated_date is None:
                    logger.warning(f"No git history found for {doc_file_path}")
                    continue
            else:
                rated_date = get_last_verified_date(doc_file_path)
            dated_doc_files.append((rated_date, doc_file_path))

    dated_doc_files.sort(
        key=lambda dated_doc_file: (dated_doc_file[0], dated_doc_file[1]),
        reverse=parsed_arguments.reverse_sort,
    )

    for rated_date, doc_file_path in dated_doc_files:
        print(f"{rated_date} {doc_file_path.relative_to(Path.cwd())}")


def init_arg_parser():
    """
    Initializes and configures the argument parser for the script.

    Returns:
        An instance of `argparse.ArgumentParser`.
    """
    arg_parser_instance = argparse.ArgumentParser(
        description="List feature_topic/use_case docs sorted by a date field.",
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
    arg_parser_instance.set_defaults(sort_field="last_verified")
    arg_parser_instance.add_argument(
        "--reverse_sort",
        "-r",
        dest="reverse_sort",
        action="store_true",
        help="Reverse the selected sort order.",
    )
    return arg_parser_instance


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
