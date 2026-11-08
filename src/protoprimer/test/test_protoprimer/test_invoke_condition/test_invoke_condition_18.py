"""
Scenario: `InvokeCondition.venv_moved_or_copied`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    _StateStride,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_moved_repo_with_venv_fails_without_hint(tmp_path):
    assert InvokeCondition.venv_moved_or_copied.test_file_basename == "test_invoke_condition_18.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        move_result = container.run("mv /work /moved", work_dir="/")
        assert move_result.exit_code == 0, str(move_result)
        result = container.run("./cmd/echo_app hi", work_dir="/moved")

    # TODO: FT_64_09_03_66.invoke_condition.md: detect that `venv` belongs to another path and hint `reset` (the hint to run `boot` below is misleading):
    assert result.exit_code != 0, str(result)
    assert f"Failed to import `local_doc` at [{_StateStride.stride_py_venv.name}]" in result.stderr, str(result)
