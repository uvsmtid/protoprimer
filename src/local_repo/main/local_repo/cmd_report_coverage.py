from __future__ import annotations

import argparse
import logging

from local_repo.sub_proc_util import get_command_code

logger = logging.getLogger()


def custom_main():
    """
    See also:
    .github/workflows/cover.yaml
    """

    parsed_args = init_arg_parser().parse_args()

    get_command_code(
        "coverage erase         --rcfile=./gconf/coveragerc.ini",
    )
    get_command_code(
        "coverage run           --rcfile=./gconf/coveragerc.ini --module pytest ./src/neoprimer/test/",
    )
    get_command_code(
        "coverage run           --rcfile=./gconf/coveragerc.ini --module pytest ./src/protoprimer/test/",
    )
    get_command_code(
        "coverage combine       --rcfile=./gconf/coveragerc.ini",
    )

    get_command_code(
        "coverage report        --rcfile=./gconf/coveragerc.ini",
    )
    get_command_code(
        "coverage xml           --rcfile=./gconf/coveragerc.ini",
    )


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Report coverage.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
