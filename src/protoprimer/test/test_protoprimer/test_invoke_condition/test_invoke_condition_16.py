"""
Scenario: `InvokeCondition.venv_broken_or_dangling`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_15,
)


def test_dangling_venv_python_fails_with_raw_file_not_found(tmp_path):
    assert InvokeCondition.venv_broken_or_dangling.test_file_basename == "test_invoke_condition_16.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        # Remove `python` installed by `uv` (the `venv/bin/python` points to it):
        container.run("rm -rf /root/.local/share/uv/python")
        result = container.run("./cmd/echo_app hi")

    # TODO: FT_64_09_03_66.invoke_condition.md: fail with a message about the broken `venv` (and `reset` hint) instead of the raw error:
    assert result.exit_code != 0, str(result)
    assert "FileNotFoundError" in result.stderr, str(result)
    assert "/work/venv/bin/python" in result.stderr, str(result)
