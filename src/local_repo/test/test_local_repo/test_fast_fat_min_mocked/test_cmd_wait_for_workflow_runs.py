import sys
from unittest.mock import patch

import pytest

from local_repo import cmd_wait_for_workflow_runs
from local_repo.cmd_wait_for_workflow_runs import (
    custom_main,
    find_not_ready,
    get_workflow_file_rel_path,
    wait_for_workflow_runs,
)
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_wait_for_workflow_runs.__name__)


def make_run(
    workflow_name: str,
    status: str,
) -> dict:
    return {
        "path": get_workflow_file_rel_path(workflow_name),
        "status": status,
    }


@pytest.mark.parametrize(
    "workflow_runs, expected_not_ready",
    [
        pytest.param([make_run("a", "completed"), make_run("b", "completed")], {}, id="all_completed"),
        pytest.param([make_run("a", "completed")], {"b": "no runs yet"}, id="missing_run"),
        pytest.param([make_run("a", "completed"), make_run("b", "in_progress")], {"b": "not completed"}, id="in_progress"),
        pytest.param([make_run("a", "completed"), make_run("b", "completed"), make_run("b", "queued")], {"b": "not completed"}, id="any_rerun_not_completed"),
        pytest.param([make_run("a", "completed"), make_run("b", "completed"), make_run("other", "in_progress")], {}, id="other_workflows_ignored"),
        pytest.param([], {"a": "no runs yet", "b": "no runs yet"}, id="no_runs"),
    ],
)
def test_find_not_ready(workflow_runs, expected_not_ready):
    assert find_not_ready(workflow_runs, ["a", "b"]) == expected_not_ready


@patch("time.sleep")
@patch.object(cmd_wait_for_workflow_runs, "get_workflow_runs")
def test_wait_returns_when_all_ready(mock_get_workflow_runs, mock_sleep):

    # given:

    mock_get_workflow_runs.side_effect = [
        [make_run("a", "in_progress")],
        [make_run("a", "completed")],
    ]

    # when:

    is_ready = wait_for_workflow_runs("owner/name", "sha", ["a"], timeout_sec=3600, poll_sec=5)

    # then:

    assert is_ready is True
    assert mock_get_workflow_runs.call_count == 2
    mock_sleep.assert_called_once_with(5)
    mock_get_workflow_runs.assert_called_with("owner/name", "sha")


@patch("time.sleep")
@patch.object(cmd_wait_for_workflow_runs, "get_workflow_runs", return_value=[make_run("a", "in_progress")])
def test_wait_times_out(mock_get_workflow_runs, mock_sleep):

    # when:

    is_ready = wait_for_workflow_runs("owner/name", "sha", ["a"], timeout_sec=-1, poll_sec=5)

    # then:

    assert is_ready is False
    mock_sleep.assert_not_called()


@pytest.mark.parametrize("is_ready, expected_exit_code", [(True, 0), (False, 1)])
def test_custom_main_exit_code(is_ready, expected_exit_code):

    with patch.object(sys, "argv", ["wait_for_workflow_runs", "--repo", "owner/name", "--commit_sha", "sha", "a", "b"]), patch.object(cmd_wait_for_workflow_runs, "wait_for_workflow_runs", return_value=is_ready) as mock_wait:
        with pytest.raises(SystemExit) as exit_info:
            custom_main()

    assert exit_info.value.code == expected_exit_code
    mock_wait.assert_called_once_with("owner/name", "sha", ["a", "b"], 40 * 60, 30)
