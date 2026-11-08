"""
Scenario: `InvokeCondition.py_required_not_found`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_14,
)


def test_no_python_found_for_required_version_fails_with_raw_type_error(tmp_path):
    assert InvokeCondition.py_required_not_found.test_file_basename == "test_invoke_condition_04.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        # No `python*` in `PATH`: neither the selector nor the basename search can find any:
        result = container.run("PATH=/nonexistent /usr/local/bin/python3 ./prime --env dst/test_python_max")

    # TODO: FT_64_09_03_66.invoke_condition.md: fail right after the search with a message (required version, basenames tried, `PATH`) and hints:
    assert result.exit_code != 0, str(result)
    assert "TypeError: expected str, bytes or os.PathLike object, not NoneType" in result.stderr, str(result)
