from __future__ import annotations

import logging
import os
import sys

from protoprimer.primer_kernel import (
    ConfLeap,
    DefaultFileLogFormatter,
    DefaultStderrLogFormatter,
    EnvState,
    get_config,
    get_default_start_id,
)

logger: logging.Logger = logging.getLogger()


def configure_stderr_log_handler(
    log_level: int = logging.WARNING,
) -> logging.StreamHandler:
    """
    UC_81_50_97_17.do_not_reuse_logger.md
    """
    logger.setLevel(logging.NOTSET)
    log_handler = logging.StreamHandler(sys.stderr)
    log_handler.setFormatter(DefaultStderrLogFormatter(log_level))
    log_handler.setLevel(log_level)
    logger.addHandler(log_handler)
    return log_handler


def configure_file_log_handler(
    file_path: str,
    log_level: int = logging.INFO,
) -> logging.FileHandler:
    """
    UC_81_50_97_17.do_not_reuse_logger.md
    """
    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True,
    )
    log_handler = logging.FileHandler(file_path)
    log_handler.setFormatter(DefaultFileLogFormatter())
    log_handler.setLevel(log_level)
    logger.addHandler(log_handler)
    return log_handler


def configure_script(
    script_basename: str,
) -> dict:
    configure_stderr_log_handler(logging.INFO)

    derived_data: dict = get_config(ConfLeap.leap_derived)

    log_dir_abs_path: str = derived_data[EnvState.state_local_log_dir_abs_path_inited.name]

    start_id: str = get_default_start_id()
    log_file_abs_path = os.path.join(
        log_dir_abs_path,
        f"{script_basename}.{start_id}.log",
    )
    configure_file_log_handler(
        log_file_abs_path,
        logging.INFO,
    )

    return derived_data
