"""
Scenario: `InvokeCondition.venv_with_system_site_packages`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_venv_with_system_site_packages_enabled_is_silently_reused(tmp_path):
    assert InvokeCondition.venv_with_system_site_packages.test_file_basename == "test_invoke_condition_19.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        container.run("sed -i 's/include-system-site-packages = false/include-system-site-packages = true/' venv/pyvenv.cfg")
        result = container.run(boot_max_script)
        pyvenv_cfg = container.run("cat venv/pyvenv.cfg")

    # TBD: reject (or re-create) such a `venv`:
    assert result.exit_code == 0, str(result)
    assert "include-system-site-packages = true" in pyvenv_cfg.stdout, str(pyvenv_cfg)
