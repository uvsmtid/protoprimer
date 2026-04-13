"""
See: FT_17_41_51_83.private_artifact_repo.md
"""

import argparse
import subprocess
from argparse import ArgumentParser


def init_arg_parser() -> ArgumentParser:
    arg_parser = argparse.ArgumentParser(description="Manage Google Cloud Artifact Registry repositories.")
    sub_parsers = arg_parser.add_subparsers(dest="command")

    # ===
    # Create command:
    create_parser = sub_parsers.add_parser(
        "create",
        help="Create a repository.",
    )
    create_parser.add_argument(
        "--description",
        default="Test Python package repository",
        help="The description of the repository.",
    )
    populate_common_args(create_parser)
    create_parser.set_defaults(func=create_repo)

    # ===
    # Delete command:
    delete_parser = sub_parsers.add_parser(
        "delete",
        help="Delete a repository.",
    )
    populate_common_args(delete_parser)
    delete_parser.set_defaults(func=delete_repo)

    # ===
    return arg_parser


def populate_common_args(operation_parser: ArgumentParser):
    operation_parser.add_argument(
        "repo_name",
        help="The name of the repository.",
    )
    operation_parser.add_argument(
        "--location",
        required=True,
        help="The location of the repository.",
    )
    operation_parser.add_argument(
        "--project",
        required=True,
        help="The Google Cloud project id.",
    )


def create_repo(parsed_args):
    """
    Creates a Google Cloud Artifact Registry repository.
    """

    subprocess.run(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "create",
            parsed_args.repo_name,
            f"--project={parsed_args.project}",
            "--repository-format=python",
            f"--location={parsed_args.location}",
            f"--description={parsed_args.description}",
        ]
    )

    show_repository_info(parsed_args)


def delete_repo(parsed_args):
    """
    Deletes a Google Cloud Artifact Registry repository.
    """

    show_repository_info(parsed_args)

    subprocess.run(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "delete",
            parsed_args.repo_name,
            f"--project={parsed_args.project}",
            f"--location={parsed_args.location}",
            "--quiet",
        ]
    )


def show_repository_info(parsed_args):
    subprocess.run(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "list",
            f"--project={parsed_args.project}",
        ]
    )
    subprocess.run(
        [
            "gcloud",
            "artifacts",
            "repositories",
            "describe",
            parsed_args.repo_name,
            f"--location={parsed_args.location}",
            f"--project={parsed_args.project}",
        ]
    )
    subprocess.run(
        [
            "gcloud",
            "artifacts",
            "print-settings",
            "python",
            f"--project={parsed_args.project}",
            f"--repository={parsed_args.repo_name}",
            f"--location={parsed_args.location}",
        ]
    )


def main():
    """
    The main function for the `gcloud_artifact_repo` script.
    """

    arg_parser = init_arg_parser()

    parsed_args = arg_parser.parse_args()
    if hasattr(parsed_args, "func"):
        parsed_args.func(parsed_args)
    else:
        arg_parser.print_help()


if __name__ == "__main__":
    main()
