from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    EntryFunc,
    generate_entry_script_content,
)


def test_relationship():
    assert_test_module_name_embeds_str(generate_entry_script_content.__name__)


def test_generate_entry_script_content_no_env_vars():

    # given:

    module_name = "my_module"
    func_name = "my_func"

    # when:

    generated_content = generate_entry_script_content(
        EntryFunc.func_boot_env.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        module_name,
        func_name,
    )

    # then:

    assert 'os.environ["' not in generated_content


def test_generate_entry_script_content_with_env_vars():

    # given:

    module_name = "my_module"
    func_name = "my_func"
    env_vars = {"MY_VAR": "my_value"}

    # when:

    generated_content = generate_entry_script_content(
        EntryFunc.func_boot_env.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        module_name,
        func_name,
        env_vars,
    )

    # then:

    assert '    os.environ["MY_VAR"] = "my_value"' in generated_content
    assert '     os.environ["MY_VAR"] = "my_value"' not in generated_content


def test_generate_entry_script_content_empty_main_func():

    # given:

    # FT_21_75_54_18.instant_scenario.md: no DAG extension:
    module_name = None
    func_name = None

    # when:

    generated_content = generate_entry_script_content(
        EntryFunc.func_boot_env.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        module_name,
        func_name,
    )

    # then:

    assert f'proto_kernel.{EntryFunc.func_boot_env.value}("{ConfConstGeneral.default_proto_main}")' in generated_content
    assert "None" not in generated_content.split("if __name__", 1)[1]
