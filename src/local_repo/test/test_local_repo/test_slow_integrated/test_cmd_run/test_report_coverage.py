from local_repo.sub_proc_util import (
    get_command_code,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.repo_tree import change_to_known_repo_path

file_name = "report_coverage"


# noinspection PyPep8Naming
def test_relationship():
    assert_test_module_name_embeds_str(file_name)


def test_cmd_run():

    with change_to_known_repo_path("."):
        get_command_code(f"./cmd/{file_name} -h")


def test_read_tests_file(tmp_path):
    from local_repo.cmd_report_coverage import read_tests_file

    tests_file = tmp_path / "tests.txt"
    tests_file.write_text("# comment\n\n  src/a/test_a.py  \nsrc/b\n  # indented comment\n")

    assert read_tests_file(str(tests_file)) == ["src/a/test_a.py", "src/b"]
