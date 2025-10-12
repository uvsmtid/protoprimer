from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.proto_generator import generate_entry_script_content


def test_relationship():
    assert_test_module_name_embeds_str(generate_entry_script_content.__name__)


def test_generate_entry_script_content_no_env_vars():
    # given:
    module_name = "my_module"
    func_name = "my_func"

    # when:
    result = generate_entry_script_content(module_name, func_name)

    # then:
    assert 'os.environ["' not in result


def test_generate_entry_script_content_with_env_vars():
    # given:
    module_name = "my_module"
    func_name = "my_func"
    env_vars = {"MY_VAR": "my_value"}

    # when:
    result = generate_entry_script_content(module_name, func_name, env_vars)

    # then:
    assert 'os.environ["MY_VAR"] = "my_value"' in result
