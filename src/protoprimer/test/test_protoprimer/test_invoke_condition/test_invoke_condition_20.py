"""
Scenario: `InvokeCondition.pkg_system_wide`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_system_wide_protoprimer_is_neither_used_nor_accepted_as_proto_kernel(tmp_path):
    assert InvokeCondition.pkg_system_wide.test_file_basename == "test_invoke_condition_20.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        install_result = container.run("pip install protoprimer")
        assert install_result.exit_code == 0, str(install_result)

        boot_result = container.run(boot_max_script)
        venv_module = container.run('./venv/bin/python -c "import protoprimer; print(protoprimer.__file__)"')
        from_site_packages = container.run("python -m protoprimer.primer_kernel --env dst/test_python_max")

    assert boot_result.exit_code == 0, str(boot_result)
    assert venv_module.stdout.strip().startswith("/work/"), str(venv_module)
    assert from_site_packages.exit_code != 0, str(from_site_packages)
    assert "cannot be from site packages" in from_site_packages.stderr, str(from_site_packages)
