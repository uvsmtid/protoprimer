# FT_85_17_35_21.boot_env.md: see also `cmd_start_app_example.py`
from __future__ import annotations

import logging

from protoprimer.primer_kernel import (
    run_boot_env_client_func,
)

logger = logging.getLogger()


def custom_boot_env_main():
    run_boot_env_client_func(lambda: print("Hello, world!"))


if __name__ == "__main__":
    custom_boot_env_main()
