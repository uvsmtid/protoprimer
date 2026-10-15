from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ShellDriverSh,
    ShellType,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ShellDriverSh.__name__,
    )


def test_get_type():
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    shell_type = driver.get_type()
    # then:
    assert shell_type == ShellType.shell_sh


def test_get_init_file_basename():
    # given:
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    basename = driver.get_init_file_basename()
    # then:
    assert basename == ".shrc"


def test_configure_interactive_shell(fs):
    # given:
    fs.create_dir("/fake/cache/sh")
    driver = ShellDriverSh(
        shell_abs_path="/bin/sh",
        shell_env_vars={},
        cache_dir_abs_path="/fake/cache",
    )
    # when:
    driver.configure_interactive_shell(False)
    # then:
    assert driver.shell_env_vars["ENV"] == "/fake/cache/sh/.shrc"
    assert driver.shell_args == ["/bin/sh"]
