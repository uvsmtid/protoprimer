import sys
from unittest.mock import patch

import pytest

from local_repo import cmd_wait_for_workflow_runs
from local_repo.cmd_wait_for_workflow_runs import (
    custom_main,
    find_not_ready,
    find_uploading_workflow_names,
    get_workflow_file_rel_path,
    wait_for_workflow_runs,
)
from local_test.invoke_condition_helper import get_repo_root_abs_path
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


def write_file(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_find_uploading_workflow_names(tmp_path):

    # given:

    workflows_dir = tmp_path / ".github" / "workflows"
    actions_dir = tmp_path / ".github" / "actions"
    write_file(actions_dir / "with_upload" / "action.yaml", "steps:\n    -   uses: x/y@v1\n        with:\n            parallel: true\n")
    write_file(actions_dir / "no_upload" / "action.yaml", "steps:\n    -   run: echo\n")
    write_file(workflows_dir / "direct.yaml", "steps:\n    -   uses: x/y@v1\n        with:\n            parallel: true\n")
    write_file(workflows_dir / "via_action.yaml", "steps:\n    -   uses: ./.github/actions/with_upload\n        with:\n            level: min\n")
    write_file(workflows_dir / "via_other_action.yaml", "steps:\n    -   uses: ./.github/actions/no_upload\n")
    write_file(workflows_dir / "commented.yaml", "steps:\n    # parallel: true\n    -   run: echo\n")
    write_file(workflows_dir / "closing.yaml", "steps:\n    -   uses: x/y@v1\n        with:\n            parallel-finished: true\n")
    write_file(workflows_dir / "other.yaml", "steps:\n    -   run: echo\n")

    # then:

    assert find_uploading_workflow_names(tmp_path) == ["direct", "via_action"]


def test_find_uploading_workflow_names_of_this_repo():

    # when:

    workflow_names = find_uploading_workflow_names(get_repo_root_abs_path())

    # then: the closing workflow does not wait for itself, and all test workflows are found

    assert "cover_finish" not in workflow_names
    assert "test_contract_compatibility" in workflow_names
    assert "test_invoke_condition" in workflow_names
    assert "test_py_min_linux" in workflow_names


def test_custom_main_discovers_workflows_without_names(tmp_path):

    # given:

    write_file(tmp_path / ".github" / "workflows" / "found.yaml", "steps:\n    -   uses: x/y@v1\n        with:\n            parallel: true\n")

    with patch.object(sys, "argv", ["wait_for_workflow_runs", "--repo", "owner/name", "--commit_sha", "sha", "--repo_dir", str(tmp_path)]), patch.object(cmd_wait_for_workflow_runs, "wait_for_workflow_runs", return_value=True) as mock_wait:

        # when:

        with pytest.raises(SystemExit) as exit_info:
            custom_main()

    # then:

    assert exit_info.value.code == 0
    mock_wait.assert_called_once_with("owner/name", "sha", ["found"], 40 * 60, 30)


def test_custom_main_fails_loudly_when_nothing_to_wait_for(tmp_path):

    (tmp_path / ".github" / "workflows").mkdir(parents=True)

    with patch.object(sys, "argv", ["wait_for_workflow_runs", "--repo", "owner/name", "--commit_sha", "sha", "--repo_dir", str(tmp_path)]):
        with pytest.raises(AssertionError):
            custom_main()
