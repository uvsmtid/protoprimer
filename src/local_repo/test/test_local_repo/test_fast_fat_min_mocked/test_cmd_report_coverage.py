import sys
from unittest.mock import (
    call,
    patch,
)

import pytest

from local_repo import cmd_report_coverage
from local_repo.cmd_report_coverage import (
    custom_main,
    default_test_dir_rel_paths,
    read_tests_file,
    rcfile_rel_path,
    run_coverage,
)
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_report_coverage.__name__)


def test_read_tests_file(tmp_path):

    # given:

    tests_file = tmp_path / "tests.txt"
    tests_file.write_text("# comment\n\n  src/a/test_a.py  \nsrc/b\n  # indented comment\n")

    # then:

    assert read_tests_file(str(tests_file)) == ["src/a/test_a.py", "src/b"]


@patch("subprocess.run")
def test_run_coverage_puts_rcfile_before_args_of_the_run_program(mock_run):

    # given:

    mock_run.return_value.returncode = 3

    # when:

    exit_code = run_coverage("run", "--module", "pytest", "some/test_path.py")

    # then:

    assert exit_code == 3
    # `--rcfile` after `pytest` args would be passed to `pytest`:
    mock_run.assert_called_once_with([sys.executable, "-m", "coverage", "run", f"--rcfile={rcfile_rel_path}", "--module", "pytest", "some/test_path.py"])


@pytest.mark.parametrize(
    "cli_args, expected_calls",
    [
        pytest.param(
            [],
            [
                call("erase"),
                call("run", "--module", "pytest", *default_test_dir_rel_paths),
                call("combine"),
                call("report"),
                call("xml"),
            ],
            id="default_dirs_report_and_xml",
        ),
        pytest.param(
            ["--all_tests", "--lcov_file", "out.lcov"],
            [
                call("erase"),
                call("run", "--module", "pytest"),
                call("combine"),
                call("lcov", "--fail-under=0", "-o", "out.lcov"),
            ],
            id="all_tests_lcov",
        ),
        pytest.param(
            ["--all_tests", "path_ignored_by_all_tests"],
            [
                call("erase"),
                call("run", "--module", "pytest"),
                call("combine"),
                call("report"),
                call("xml"),
            ],
            id="all_tests_wins_over_paths",
        ),
        pytest.param(
            ["path_a", "path_b", "--lcov_file", "out.lcov"],
            [
                call("erase"),
                call("run", "--module", "pytest", "path_a", "path_b"),
                call("combine"),
                call("lcov", "--fail-under=0", "-o", "out.lcov"),
            ],
            id="paths_lcov",
        ),
    ],
)
def test_custom_main_calls(cli_args, expected_calls):

    # given:

    with patch.object(sys, "argv", ["report_coverage"] + cli_args), patch.object(cmd_report_coverage, "run_coverage", return_value=0) as mock_run_coverage:

        # when:

        with pytest.raises(SystemExit) as exit_info:
            custom_main()

    # then:

    assert exit_info.value.code == 0
    assert mock_run_coverage.call_args_list == expected_calls


def test_custom_main_merges_tests_file_and_paths(tmp_path):

    # given:

    tests_file = tmp_path / "tests.txt"
    tests_file.write_text("# comment\nfrom_file_a\nfrom_file_b\n")

    with patch.object(sys, "argv", ["report_coverage", "--tests_file", str(tests_file), "path_a"]), patch.object(cmd_report_coverage, "run_coverage", return_value=0) as mock_run_coverage:

        # when:

        with pytest.raises(SystemExit):
            custom_main()

    # then:

    assert mock_run_coverage.call_args_list[1] == call("run", "--module", "pytest", "path_a", "from_file_a", "from_file_b")


@pytest.mark.parametrize(
    "failing_step_index, expected_call_count",
    [
        (0, 1),  # erase
        (1, 2),  # run: no coverage is combined or reported for failed tests
        (2, 3),  # combine
    ],
)
def test_custom_main_stops_on_first_failure(failing_step_index, expected_call_count):

    # given:

    exit_codes = [0, 0, 0, 0, 0]
    exit_codes[failing_step_index] = 7

    with patch.object(sys, "argv", ["report_coverage", "--all_tests", "--lcov_file", "out.lcov"]), patch.object(cmd_report_coverage, "run_coverage", side_effect=exit_codes) as mock_run_coverage:

        # when:

        with pytest.raises(SystemExit) as exit_info:
            custom_main()

    # then:

    assert exit_info.value.code == 7
    assert mock_run_coverage.call_count == expected_call_count
