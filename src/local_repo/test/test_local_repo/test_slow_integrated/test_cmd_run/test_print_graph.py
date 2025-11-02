import pathlib

from local_repo.sub_proc_util import (
    get_command_code,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.repo_tree import change_to_known_repo_path

file_name = "print_graph"


# noinspection PyPep8Naming
def test_relationship():
    assert_test_module_name_embeds_str(file_name)


def test_cmd_run():

    with change_to_known_repo_path("."):
        get_command_code(f"./cmd/{file_name} -h")
