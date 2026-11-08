"""
Scenario: `InvokeCondition.venv_wrong_active`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_15,
)


def test_other_activated_venv_is_escaped_and_left_untouched(tmp_path):
    assert InvokeCondition.venv_wrong_active.test_file_basename == "test_invoke_condition_10.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        result = container.run(f"python -m venv /tmp/other && . /tmp/other/bin/activate && {boot_max_script}")
        venv_prefix = container.run('./venv/bin/python -c "import sys; print(sys.prefix)"')
        other_packages = container.run("/tmp/other/bin/python -m pip list --format=freeze")

    assert result.exit_code == 0, str(result)
    assert venv_prefix.stdout.strip() == "/work/venv", str(venv_prefix)
    assert "protoprimer" not in other_packages.stdout, str(other_packages)
