# FT_66_02_54_56.context_isolation.md
from __future__ import annotations

import logging
import os
import sys

from protoprimer.primer_kernel import EnvVar

logger = logging.getLogger()


def custom_main():
    """
    FT_66_02_54_56.context_isolation.md
    """
    found_vars = [
        #
        (env_var, os.environ[env_var.value])
        for env_var in EnvVar
        if env_var.value in os.environ
    ]

    for env_var_key, env_var_value in found_vars:
        logger.info(f"{env_var_key.value}={env_var_value}")

    logger.info(f"`{EnvVar.__name__}` count in environ: {len(found_vars)}")

    if found_vars:
        sys.exit(1)


if __name__ == "__main__":
    custom_main()
