import os
import textwrap
from typing import Dict


def generate_entry_script_content(
    # TODO: Move this function to `protoprimer.primer_kernel`? To use `SubCommand` enum.
    sub_command: str,
    proto_kernel_abs_path: str,
    entry_script_abs_path: str,
    module_name: str,
    func_name: str,
    env_vars: Dict[str, str] = None,
) -> str:
    """
    Generates: FT_75_87_82_46.entry_script.md
    """

    env_vars_lines = ""
    if env_vars:
        env_vars_lines = "\n".join(
            [
                f'os.environ["{var_name}"] = "{var_value}"'
                for var_name, var_value in env_vars.items()
                #
            ]
        )
        env_vars_lines = textwrap.indent(env_vars_lines, "    ")

    if sub_command == "start":
        entry_func = "start_app"
    elif sub_command == "boot":
        entry_func = "boot_env"
    else:
        raise AssertionError(f"Unrecognized `sub_command` [{sub_command}]")

    proto_kernel_rel_path = os.path.relpath(
        proto_kernel_abs_path,
        os.path.dirname(entry_script_abs_path),
    )

    return f"""#!/usr/bin/env python3

def import_proto_kernel(proto_kernel_rel_path: str):
    \"""
    `protoprimer` entry script boilerplate function to import `proto_kernel`.
    \"""

    import os
    import importlib.util

    module_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(str(__file__)),
            proto_kernel_rel_path,
        ),
    )
    assert module_spec is not None
    loaded_proto_module = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(loaded_proto_module)
    return loaded_proto_module

if __name__ == "__main__":
    import os

{env_vars_lines}

    proto_kernel = import_proto_kernel("{proto_kernel_rel_path}")
    proto_kernel.{entry_func}("{module_name}:{func_name}")
"""
