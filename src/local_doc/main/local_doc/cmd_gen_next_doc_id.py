from __future__ import annotations

import argparse
import logging
import os
import random

logger = logging.getLogger(__name__)

expected_format = "PREFIX_00_00.some_name.md"


def gen_next_doc_id() -> None:
    """
    Main func to generate a doc file id.
    """

    arg_parser_instance = init_arg_parser()
    parsed_arguments = arg_parser_instance.parse_args()

    if not os.path.isdir(parsed_arguments.doc_dir):
        logger.error(f"Directory not found at {parsed_arguments.doc_dir}")
        return

    file_names_list: list[str] = [
        file_entry
        for file_entry in os.listdir(parsed_arguments.doc_dir)
        if os.path.isfile(os.path.join(parsed_arguments.doc_dir, file_entry))
    ]

    if not file_names_list:
        logger.error(f"No files found in {parsed_arguments.doc_dir}")
        return

    (
        doc_prefix_value,
        existing_ids,
        num_id_parts,
    ) = get_prefix_and_ids(
        file_names_list,
    )

    if doc_prefix_value is None:
        logger.error(
            f"Could not determine a common file prefix in {parsed_arguments.doc_dir}",
        )
        logger.error(f"Files should be in the format like `{expected_format}`")
        return

    if not existing_ids:
        logger.warning(
            f"No valid file ids found in {parsed_arguments.doc_dir}, will generate a new one."
        )

    new_id_segment_list: tuple[str, ...] = generate_next_id(
        existing_ids,
        num_id_parts,
    )
    formatted_id_string: str = "_".join(new_id_segment_list)
    print(f"{doc_prefix_value}_{formatted_id_string}")


def init_arg_parser():
    """
    Initializes and configures the argument parser for the script.

    Returns:
        An instance of `argparse.ArgumentParser`.
    """
    arg_parser_instance = argparse.ArgumentParser(
        description=(
            "Generate a new documentation file id based on existing files in a directory "
            "using Lexicographical Frequency Minimization with randomization."
        ),
    )
    arg_parser_instance.add_argument(
        "doc_dir",
        type=str,
        help="The directory containing documentation files.",
    )
    return arg_parser_instance


def get_prefix_and_ids(
    file_names_list: list[str],
) -> tuple[
    str | None,
    set[tuple[str, ...]],
    int,
]:
    """
    Parses a list of file names which should be in the format like `PREFIX_NN_NN_NN_NN.some_name.md`.

    Extracts:
    *   a set of existing ids,
    *   a common prefix,
    *   and the number of parts in each id.

    Args:
        file_names_list: a list of filenames to parse.

    Returns:
        A tuple containing:
        *   The common prefix (e.g., "PREFIX"), or `None` if no valid files are found.
        *   A set of existing id tuples (e.g., {("01", "02", "03", "04"), ("05", "06", "07", "08")}).
        *   The number of numerical parts in each id (e.g., 4).
    """
    doc_prefix: str | None = None
    num_id_parts: int = 0
    existing_ids: set[tuple[str, ...]] = set()

    for file_name_str in file_names_list:
        file_parts = file_name_str.split(".")[0].split("_")
        if len(file_parts) < 2:
            continue

        file_prefix_str = file_parts[0]
        id_parts_tuple = tuple(file_parts[1:])

        if not all(id_part.isdigit() for id_part in id_parts_tuple):
            continue

        if doc_prefix is None:
            doc_prefix = file_prefix_str
            num_id_parts = len(id_parts_tuple)

        if file_prefix_str != doc_prefix:
            logger.warning(
                f"Skipping file `{file_name_str}` with mismatched prefix. Expected `{doc_prefix}`, found `{file_prefix_str}`."
            )
            continue

        if len(id_parts_tuple) != num_id_parts:
            logger.warning(
                f"Skipping file `{file_name_str}` with inconsistent id length. Expected {num_id_parts} parts, found {len(id_parts_tuple)}."
            )
            continue

        existing_ids.add(id_parts_tuple)

    return doc_prefix, existing_ids, num_id_parts


def _generate_random_id(
    num_id_parts: int,
) -> tuple[str, ...]:
    """
    Generates a completely random id.

    Args:
        num_id_parts: The number of parts the id should have.

    Returns:
        A tuple of strings, where each string is a two-digit number part of the new id.
    """
    if num_id_parts == 0:
        return tuple()
    return tuple(f"{random.randint(0, 99):02d}" for _ in range(num_id_parts))


def generate_next_id(
    existing_ids: set[tuple[str, ...]],
    num_id_parts: int,
) -> tuple[str, ...]:
    """
    Generates a new random id using digit-by-digit Lexicographical Frequency Minimization.

    Args:
        existing_ids: A set of existing id tuples.
        num_id_parts: The number of parts in the new id.

    Returns:
        A new id as a tuple of strings (e.g., ("25", "67", "57", "18")).
    """
    if num_id_parts == 0:
        return tuple()

    if not existing_ids:
        return _generate_random_id(num_id_parts)

    existing_id_strings: set[str] = {"".join(id_tuple) for id_tuple in existing_ids}
    num_digits = num_id_parts * 2

    max_attempts = 100
    for _ in range(max_attempts):
        new_id_digits: list[str] = []
        candidate_id_strings: list[str] = list(existing_id_strings)

        for i in range(num_digits):
            freq_map: dict[str, int] = {str(j): 0 for j in range(10)}
            for id_str in candidate_id_strings:
                digit = id_str[i]
                freq_map[digit] += 1

            min_freq = min(freq_map.values())
            least_frequent_digits = [
                digit for digit, freq in freq_map.items() if freq == min_freq
            ]

            chosen_digit = random.choice(least_frequent_digits)
            new_id_digits.append(chosen_digit)

            candidate_id_strings = [
                id_str for id_str in candidate_id_strings if id_str[i] == chosen_digit
            ]

        new_id_str = "".join(new_id_digits)

        if new_id_str not in existing_id_strings:
            new_id_parts = [new_id_str[j : j + 2] for j in range(0, num_digits, 2)]
            return tuple(new_id_parts)

    logger.warning("Could not generate a unique ID, falling back to random.")
    return _generate_random_id(num_id_parts)
