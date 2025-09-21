import os.path

from packaging.version import Version

from local_test.toml_handler import load_toml_data
from protoprimer.primer_kernel import ConfConstClient


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

    toml_path: str = str(
        os.path.join(
            # 3 levels up without basename: ../../../.
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(__file__),
                    ),
                ),
            ),
            module_obj.__name__,
            ConfConstClient.default_pyproject_toml_basename,
        )
    )

    # when:

    toml_data = load_toml_data(toml_path)

    # then:

    return toml_data["project"]["version"] == module_version


def extract_package_version(
    pip_freeze_output: str,
    package_name: str,
) -> Version:
    for line in pip_freeze_output.splitlines():
        if f"{package_name}==" in line:
            version_str = line.split("==")[1]
            return Version(version_str)
    raise ValueError(f"package [{package_name}] not found in pip freeze output")
