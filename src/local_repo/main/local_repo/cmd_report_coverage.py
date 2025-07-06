from __future__ import annotations

import logging

from local_repo.sub_proc_util import get_command_code

logger = logging.getLogger()


def main():
    get_command_code(
        "coverage run --branch --source=./src/protoprimer/main/ --module unittest discover --start-directory ./src/protoprimer/test/"
    )
    get_command_code("coverage report --show-missing --no-skip-covered")
    get_command_code("coverage xml")


if __name__ == "__main__":
    main()
