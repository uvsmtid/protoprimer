from __future__ import annotations

import logging

from local_repo.sub_proc_util import get_command_code

logger = logging.getLogger()


def main():
    """
    See also:
    .github/workflows/cover.yaml
    """

    get_command_code(
        "coverage erase         --rcfile=./conf_client/coveragerc.ini",
    )
    get_command_code(
        "coverage run           --rcfile=./conf_client/coveragerc.ini --module pytest ./src/neoprimer/test/",
    )
    get_command_code(
        "coverage run           --rcfile=./conf_client/coveragerc.ini --module pytest ./src/protoprimer/test/",
    )
    get_command_code(
        "coverage combine       --rcfile=./conf_client/coveragerc.ini",
    )

    get_command_code(
        "coverage report        --rcfile=./conf_client/coveragerc.ini",
    )
    get_command_code(
        "coverage xml           --rcfile=./conf_client/coveragerc.ini",
    )


if __name__ == "__main__":
    main()
