"""
The schema of `protoprimer` config files (for testing only): one model per `ConfLeap` which has a config file.

*   Field names are literals (not taken from `protoprimer`): the schema does not depend on the code it describes.
*   Fields are optional: configs are partial (defaults are applied for the missing ones).
*   Extra fields are ignored: a new field in the new code's config is backward-compatible.

See: FT_78_72_23_04.backward_compatibility.md
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class SchemaModel(BaseModel):

    model_config = ConfigDict(extra="ignore")


class ProjectDescriptor(SchemaModel):
    build_root_dir_rel_path: Optional[str] = None
    install_extras: Optional[List[str]] = None
    install_group: Optional[str] = None


class InstallGroupSpec(SchemaModel):
    extra_command_args: Optional[List[str]] = None


class CommonConf(SchemaModel):
    """
    Common overridable `global` and `local` fields (FT_23_37_64_44.global_vs_local.md).
    """

    required_python_version: Optional[str] = None
    python_selector_file_rel_path: Optional[str] = None
    local_venv_dir_rel_path: Optional[str] = None
    local_log_dir_rel_path: Optional[str] = None
    local_run_dir_rel_path: Optional[str] = None
    local_tmp_dir_rel_path: Optional[str] = None
    local_cache_dir_rel_path: Optional[str] = None
    venv_driver: Optional[str] = None
    version_constraints_file_basename: Optional[str] = None
    project_descriptors: Optional[List[ProjectDescriptor]] = None
    install_specs: Optional[List[Dict[str, InstallGroupSpec]]] = None


class ConfPrimer(SchemaModel):
    """
    `ConfLeap.leap_primer`
    """

    ref_root_dir_rel_path: Optional[str] = None
    global_conf_dir_rel_path: Optional[str] = None


class ConfClient(CommonConf):
    """
    `ConfLeap.leap_client`
    """

    local_conf_symlink_rel_path: Optional[str] = None
    default_env_dir_rel_path: Optional[str] = None


class ConfEnv(CommonConf):
    """
    `ConfLeap.leap_env`
    """


def find_known_field_names() -> List[str]:
    """
    Every field name known to any model of the schema (top-level and nested).
    """

    known_field_names = set()
    for model_class in [ConfPrimer, ConfClient, ConfEnv, ProjectDescriptor, InstallGroupSpec]:
        known_field_names.update(model_class.model_fields)
    return sorted(known_field_names)
