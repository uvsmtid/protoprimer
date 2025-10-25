def generate_entry_script_content(
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

    return f"""#!/usr/bin/env python3
import os
if __name__ == "__main__":
{env_vars_lines}
    proto_kernel_rel_path = "./proto_code/proto_kernel.py"

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # Boilerplate to import `proto_kernel` from `protoprimer`
    import os
    import importlib.util

    proto_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(__file__),
            proto_kernel_rel_path,
        ),
    )
    proto_kernel = importlib.util.module_from_spec(proto_spec)
    proto_spec.loader.exec_module(proto_kernel)
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    proto_kernel.run_main(
        "{module_name}",
        "{func_name}",
    )
"""
