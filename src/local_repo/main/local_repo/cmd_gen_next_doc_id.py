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
        description="Generate a new documentation file id based on existing files in a directory.",
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


def _find_best_prefix(
    joined_num_pairs_set: set[str],
    num_id_parts: int,
) -> str | None:
    """
    Finds the best prefix for a new id based on existing ones.

    The "best" prefix is determined by finding the shortest prefix length
    that has the minimum frequency of occurrence among the existing ids.

    Args:
        joined_num_pairs_set: A set of existing ids, where each id is a string of concatenated number pairs.
        num_id_parts: The number of parts in the id.

    Returns:
        A string representing the best prefix, or `None` if no suitable prefix is found.
    """
    min_len_found = -1
    min_freq_val = -1
    candidate_prefixes: list[str] = []

    max_len_val = num_id_parts * 2
    for prefix_len_val in range(1, max_len_val + 1):
        if min_len_found != -1 and prefix_len_val > min_len_found:
            break

        prefix_freq_dict: dict[str, int] = {
            str(index_val).zfill(prefix_len_val): 0
            for index_val in range(10**prefix_len_val)
        }

        for joined_num_pairs in joined_num_pairs_set:
            if len(joined_num_pairs) >= prefix_len_val:
                current_prefix = joined_num_pairs[:prefix_len_val]
                if current_prefix in prefix_freq_dict:
                    prefix_freq_dict[current_prefix] += 1

        sorted_prefixes = sorted(prefix_freq_dict.items(), key=lambda item: item[1])
        current_min_freq = sorted_prefixes[0][1]

        if min_freq_val == -1 or current_min_freq < min_freq_val:
            min_freq_val = current_min_freq
            min_len_found = prefix_len_val
            candidate_prefixes = [
                prefix_val
                for prefix_val, freq_val in sorted_prefixes
                if freq_val == min_freq_val
            ]
        elif current_min_freq == min_freq_val and min_len_found == prefix_len_val:
            candidate_prefixes.extend(
                [
                    prefix_val
                    for prefix_val, freq_val in sorted_prefixes
                    if freq_val == min_freq_val
                ]
            )

    if not candidate_prefixes:
        return None

    return random.choice(candidate_prefixes)


def _construct_id_from_prefix(
    id_prefix: str,
    num_id_parts: int,
) -> tuple[str, ...]:
    """
    Constructs a new id by appending random digits to a given prefix.

    Args:
        id_prefix: The prefix to use for the new id.
        num_id_parts: The total number of parts the final id should have.

    Returns:
        A tuple of strings, where each string is a two-digit number part of the new id.
    """
    remaining_len_val: int = num_id_parts * 2 - len(id_prefix)
    random_suffix_str: str = "".join(
        [str(random.randint(0, 9)) for _ in range(remaining_len_val)],
    )
    new_id_str: str = id_prefix + random_suffix_str
    new_id_parts: list[str] = [
        new_id_str[index_val : index_val + 2]
        for index_val in range(0, len(new_id_str), 2)
    ]
    return tuple(new_id_parts)


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
    Generates a new random id with a minimal unique prefix of the smallest frequency.

    Args:
        existing_ids: A set of existing id tuples.
        num_id_parts: The number of parts in the new id.

    Returns:
        A new id as a tuple of strings (e.g., ("25", "67", "57", "18")).
    """
    if not existing_ids:
        return _generate_random_id(num_id_parts)

    joined_num_pairs_set: set[str] = {
        "".join(existing_id_num_pairs) for existing_id_num_pairs in existing_ids
    }

    chosen_prefix_str = _find_best_prefix(joined_num_pairs_set, num_id_parts)

    if chosen_prefix_str is None:
        # Fallback, though unlikely with the loop limit:
        return _generate_random_id(num_id_parts)

    return _construct_id_from_prefix(chosen_prefix_str, num_id_parts)
