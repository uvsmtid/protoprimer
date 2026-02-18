from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import import_proto_module


def test_relationship():
    assert_test_module_name_embeds_str(
        import_proto_module.__name__,
    )


def test_import_proto_module_by_importing_this_test():
    """
    Tests that `import_proto_module` can load a Python file and that its contents are accessible.
    """

    # given:

    # The path to the current test file:
    current_file_path = __file__
    current_func_name = test_import_proto_module_by_importing_this_test.__name__

    # A unique module name to avoid `sys.modules` collisions:
    unique_module_name = f"{__name__}.{current_func_name}"

    # when:

    # Import the current test file as a new module.
    imported_module = import_proto_module(unique_module_name, current_file_path)

    # then:

    # The newly loaded module should contain the functions defined in this file:
    assert hasattr(imported_module, current_func_name)
    imported_function = getattr(imported_module, current_func_name)

    # The attribute should be a callable function:
    assert callable(imported_function)

    # Because the module is reloaded, it will be a different function object
    # than the currently executing one, but it should have the same name:
    assert imported_function != test_import_proto_module_by_importing_this_test
    assert imported_function.__name__ == current_func_name
