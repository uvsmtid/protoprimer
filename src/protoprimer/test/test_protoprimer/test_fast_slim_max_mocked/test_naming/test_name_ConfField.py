from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
    FilesystemObject,
    PathName,
    PathType,
    ValueName,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_test_base import (
    NamingTestBase,
)


class FieldMeta(AbstractMeta):

    def __init__(
        self,
        conf_field: ConfField,
        name_category: NameCategory,
        name_components: list[str],
    ):
        self.field_name: ConfField = conf_field
        self.name_category: NameCategory = name_category
        self.name_components: list[str] = name_components

    def get_prod_item(self):
        return self.field_name

    def extract_prod_item_value_name(self) -> str:
        return self.field_name.value

    def get_name(self):
        return self.field_name.value

    def get_category(self):
        return self.name_category

    def get_name_components(self) -> list[str]:
        return self.name_components


class FieldName(enum.Enum):

    field_ref_root_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_ref_root_dir_rel_path,
        name_category=NameCategory.category_path_field,
        name_components=[
            PathName.path_ref_root.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_global_conf_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_global_conf_dir_rel_path,
        name_category=NameCategory.category_path_field,
        name_components=[
            PathName.path_global_conf.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_local_conf_symlink_rel_path = FieldMeta(
        conf_field=ConfField.field_local_conf_symlink_rel_path,
        name_category=NameCategory.category_path_field,
        name_components=[
            PathName.path_local_conf.value,
            FilesystemObject.fs_object_symlink.value,
            PathType.path_rel.value,
        ],
    )

    field_default_env_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_default_env_dir_rel_path,
        name_category=NameCategory.category_path_field,
        name_components=[
            PathName.path_default_env.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_required_python_version = FieldMeta(
        conf_field=ConfField.field_required_python_version,
        name_category=NameCategory.category_value_field,
        name_components=[
            PathName.path_required_python.value,
            ValueName.value_version.value,
        ],
    )

    field_python_selector_file_rel_path = FieldMeta(
        conf_field=ConfField.field_python_selector_file_rel_path,
        name_category=NameCategory.category_path_field,
        name_components=[
            PathName.path_python_selector.value,
            FilesystemObject.fs_object_file.value,
            PathType.path_rel.value,
        ],
    )

    field_local_venv_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_local_venv_dir_rel_path,
        name_category=NameCategory.category_derived_path_field,
        name_components=[
            PathName.path_local_venv.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_project_descriptors = FieldMeta(
        conf_field=ConfField.field_project_descriptors,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_project_descriptors.value,
        ],
    )

    field_install_specs = FieldMeta(
        conf_field=ConfField.field_install_specs,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_install_specs.value,
        ],
    )

    field_build_root_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_build_root_dir_rel_path,
        name_category=NameCategory.category_path_arg_value,
        name_components=[
            PathName.path_build_root.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_install_extras = FieldMeta(
        conf_field=ConfField.field_install_extras,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_install_extras.value,
        ],
    )

    field_install_group = FieldMeta(
        conf_field=ConfField.field_install_group,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_install_group.value,
        ],
    )

    field_extra_command_args = FieldMeta(
        conf_field=ConfField.field_extra_command_args,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_extra_command_args.value,
        ],
    )

    field_local_log_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_local_log_dir_rel_path,
        name_category=NameCategory.category_derived_path_field,
        name_components=[
            PathName.path_local_log.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_local_tmp_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_local_tmp_dir_rel_path,
        name_category=NameCategory.category_derived_path_field,
        name_components=[
            PathName.path_local_tmp.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_local_cache_dir_rel_path = FieldMeta(
        conf_field=ConfField.field_local_cache_dir_rel_path,
        name_category=NameCategory.category_derived_path_field,
        name_components=[
            PathName.path_local_cache.value,
            FilesystemObject.fs_object_dir.value,
            PathType.path_rel.value,
        ],
    )

    field_venv_driver = FieldMeta(
        conf_field=ConfField.field_venv_driver,
        name_category=NameCategory.category_value_field,
        name_components=[
            ValueName.value_venv_driver.value,
        ],
    )


class TestFieldName(NamingTestBase):
    prod_enum = ConfField
    test_enum = FieldName
    enum_prefix: str = "field_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
