from __future__ import annotations

import os
import shutil
import sys
import logging

logger = logging.getLogger()


def is_venv():
    return sys.prefix != sys.base_prefix


def main():

    if is_venv():
        os.execv(
            # TODO: This is supposed to work (even if `PATH` is set only on `venv` activation) because `pre-commit` is installed in `~/.local/bin`:
            #       shutil.which("pre-commit")
            # TODO: But this is too specific for `cmd_` module as its `__file__` location is now in `venv`:
            #       os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # TODO: Decide what is better: using `pre-commit` path in `venv` or in `~/.local/bin`? So far, `venv` at least works (and more local/controllable for the project):
            os.path.join(
                os.path.dirname(sys.executable),
                "pre-commit",
            ),
            [
                "pre-commit",
                "run",
                "--all-files",
                "--config",
                "conf_client/pre_commit.yaml",
            ],
        )
    else:
        logger.error("not a venv")


if __name__ == "__main__":
    main()
