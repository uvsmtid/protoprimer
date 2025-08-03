import os.path

from local_test.toml_handler import load_toml_data


def verify_package_version(
    module_obj,
) -> bool:
    """
    Test that version returned for installed package matches its `pyproject.toml`.
    """

    # given:

    module_version = getattr(
        module_obj,
        "__version__",
    )

    toml_path = os.path.join(
        # 3 levels up without basename: ../../../.
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__),
                ),
            ),
        ),
        module_obj.__name__,
        "pyproject.toml",
    )

    # when:

    toml_data = load_toml_data(toml_path)

    # then:

    return toml_data["project"]["version"] == module_version
