"""
Scenario: `InvokeCondition.pkg_via_pythonpath_or_cwd`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_fake_protoprimer_in_pythonpath_is_not_imported_by_boot(tmp_path):
    assert InvokeCondition.pkg_via_pythonpath_or_cwd.test_file_basename == "test_invoke_condition_22.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        container.run("mkdir -p /tmp/fake/protoprimer && echo 'raise RuntimeError(\"fake\")' > /tmp/fake/protoprimer/__init__.py")
        result = container.run("./prime --env dst/test_python_max", env={"PYTHONPATH": "/tmp/fake"})
        venv_module = container.run('./venv/bin/python -c "import protoprimer; print(protoprimer.__file__)"')

    assert result.exit_code == 0, str(result)
    assert venv_module.stdout.strip().startswith("/work/"), str(venv_module)
