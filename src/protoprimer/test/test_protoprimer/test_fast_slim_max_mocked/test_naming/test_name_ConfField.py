from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfField,
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
    ):
        self.field_name: ConfField = conf_field
        self.name_category: NameCategory = name_category

    def get_prod_item(self):
        return self.field_name

    def extract_prod_item_value_name(self) -> str:
        return self.field_name.value

    def get_name(self):
        return self.field_name.value

    def get_category(self):
        return self.name_category


class FieldName(enum.Enum):

    field_ref_root_dir_rel_path = FieldMeta(
        ConfField.field_ref_root_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_global_conf_dir_rel_path = FieldMeta(
        ConfField.field_global_conf_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_local_conf_symlink_rel_path = FieldMeta(
        ConfField.field_local_conf_symlink_rel_path,
        NameCategory.category_path_field,
    )

    field_default_env_dir_rel_path = FieldMeta(
        ConfField.field_default_env_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_required_python_file_abs_path = FieldMeta(
        ConfField.field_required_python_file_abs_path,
        NameCategory.category_derived_path_field,
    )

    field_local_venv_dir_rel_path = FieldMeta(
        ConfField.field_local_venv_dir_rel_path,
        NameCategory.category_derived_path_field,
    )

    field_project_descriptors = FieldMeta(
        ConfField.field_project_descriptors,
        NameCategory.category_value_field,
    )

    field_build_root_dir_rel_path = FieldMeta(
        ConfField.field_build_root_dir_rel_path,
        NameCategory.category_path_arg_value,
    )

    field_install_extras = FieldMeta(
        ConfField.field_install_extras,
        NameCategory.category_value_field,
    )

    field_local_log_dir_rel_path = FieldMeta(
        ConfField.field_local_log_dir_rel_path,
        NameCategory.category_derived_path_field,
    )

    field_local_tmp_dir_rel_path = FieldMeta(
        ConfField.field_local_tmp_dir_rel_path,
        NameCategory.category_derived_path_field,
    )

    field_local_cache_dir_rel_path = FieldMeta(
        ConfField.field_local_cache_dir_rel_path,
        NameCategory.category_derived_path_field,
    )

    field_package_driver = FieldMeta(
        ConfField.field_package_driver,
        NameCategory.category_value_field,
    )


class TestFieldName(NamingTestBase):
    prod_enum = ConfField
    test_enum = FieldName
    enum_prefix: str = "field_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
