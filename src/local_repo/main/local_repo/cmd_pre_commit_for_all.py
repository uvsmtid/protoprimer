from __future__ import annotations

import argparse
import logging
import os
import sys

logger = logging.getLogger()


def main():

    parsed_args = init_arg_parser().parse_args()

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
            # TODO: Have a way to use config directory set for the protoprimer:
            "gconf/pre_commit.yaml",
        ],
    )


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description="Run `pre-commit` on all files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    return arg_parser


if __name__ == "__main__":
    main()
