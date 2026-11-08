"""
Scenario: `InvokeCondition.venv_half_created`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_empty_venv_dir_is_reused_and_fails_on_missing_pyvenv_cfg(tmp_path):
    assert InvokeCondition.venv_half_created.test_file_basename == "test_invoke_condition_17.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        container.run("mkdir venv")
        result = container.run("./prime --env dst/test_python_max")

    # TODO: FT_64_09_03_66.invoke_condition.md: detect an incomplete `venv` and re-create it (or hint `reset`):
    assert result.exit_code != 0, str(result)
    assert "pyvenv.cfg] does not exist" in result.stderr, str(result)
