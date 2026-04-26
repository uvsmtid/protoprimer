from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import SubCommand
from protoprimer.proto_generator import generate_entry_script_content


def test_relationship():
    assert_test_module_name_embeds_str(generate_entry_script_content.__name__)


def test_generate_entry_script_content_no_env_vars():

    # given:

    module_name = "my_module"
    func_name = "my_func"

    # when:

    generated_content = generate_entry_script_content(
        SubCommand.command_boot.value,
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
        SubCommand.command_boot.value,
        "/dummy/path/proto_kernel.py",
        "/dummy/path/entry.py",
        module_name,
        func_name,
        env_vars,
    )

    # then:

    assert '    os.environ["MY_VAR"] = "my_value"' in generated_content
    assert '     os.environ["MY_VAR"] = "my_value"' not in generated_content
