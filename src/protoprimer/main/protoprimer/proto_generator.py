import os


def generate_entry_script_content(
    # TODO: Move this function to `protoprimer.primer_kernel`? To use `RunMode` enum.
    run_mode: str,
    proto_kernel_abs_path: str,
    entry_script_abs_path: str,
    module_name: str,
    func_name: str,
    env_vars: dict[str, str] = None,
) -> str:
    """
    Generates: FT_75_87_82_46.entry_script.md
    """

    env_vars_lines = ""
    if env_vars:
        env_vars_lines = "\n".join(
            [
                f'    os.environ["{var_name}"] = "{var_value}"'
                for var_name, var_value in env_vars.items()
            ]
        )

    if run_mode == "start":
        entry_func = "app_starter"
    elif run_mode == "prime":
        entry_func = "env_bootstrapper"
    else:
        raise AssertionError(f"Unrecognized `run_mode` [{run_mode}]")

    proto_kernel_rel_path = os.path.relpath(
        proto_kernel_abs_path,
        os.path.dirname(entry_script_abs_path),
    )

    return f"""#!/usr/bin/env python3

import os

def import_proto_kernel(proto_kernel_rel_path: str):
    \"""
    Boilerplate function to import `proto_kernel` from the `protoprimer`.
    \"""

    import importlib.util

    module_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(__file__),
            proto_kernel_rel_path,
        ),
    )
    loaded_proto_kernel = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(loaded_proto_kernel)
    return loaded_proto_kernel

if __name__ == "__main__":
{env_vars_lines}
    proto_kernel = import_proto_kernel("{proto_kernel_rel_path}")
    proto_kernel.{entry_func}("{module_name}:{func_name}")
"""
