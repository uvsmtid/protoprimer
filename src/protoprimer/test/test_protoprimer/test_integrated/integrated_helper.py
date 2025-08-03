import logging
import os
import pathlib

import protoprimer
from local_repo.sub_proc_util import get_command_code

logger = logging.getLogger()


def switch_to_test_dir_with_plain_proto_code(
    tmp_path: pathlib.Path,
) -> None:
    """
    Creates a test dir with FT_90_65_67_62.proto_code.md.
    """

    test_dir_abs_path = tmp_path
    assert test_dir_abs_path.is_absolute()
    assert test_dir_abs_path.is_dir()
    proto_code_file_abs_path = protoprimer.primer_kernel.__file__
    proto_code_file_basename = os.path.basename(proto_code_file_abs_path)
    os.chdir(test_dir_abs_path)
    get_command_code(
        f"cp {proto_code_file_abs_path} {test_dir_abs_path}",
    )
    get_command_code(
        f"chmod u+x ./{proto_code_file_basename}",
    )
    logger.info(f"test dir: {os.getcwd()}")
