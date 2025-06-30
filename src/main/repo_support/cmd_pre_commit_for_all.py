#!/usr/bin/env python3


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
            shutil.which("pre-commit"),
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
