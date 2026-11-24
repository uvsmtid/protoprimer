import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer.primer_kernel import (
    _compose_local_conf_symlink_abs_path,
    ConfField,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _compose_local_conf_symlink_abs_path.__name__,
    )


def test_symlink_is_relative_to_ref_root():
    # when:
    result = _compose_local_conf_symlink_abs_path(
        abs_path("/ref_root"),
        {ConfField.field_local_conf_symlink_rel_path.value: "lconf"},
    )

    # then:
    assert result == abs_path("/ref_root/lconf")


def test_symlink_can_be_nested():
    # when:
    result = _compose_local_conf_symlink_abs_path(
        abs_path("/ref_root"),
        {ConfField.field_local_conf_symlink_rel_path.value: "conf/env"},
    )

    # then:
    assert os.path.normpath(result) == abs_path("/ref_root/conf/env")


def test_none_when_symlink_is_not_configured():
    # when:
    result = _compose_local_conf_symlink_abs_path(abs_path("/ref_root"), {})

    # then: there is nothing to persist the env in
    assert result is None


def test_failure_when_symlink_path_is_absolute():
    # when:
    with pytest.raises(AssertionError) as exc_info:
        _compose_local_conf_symlink_abs_path(
            abs_path("/ref_root"),
            {ConfField.field_local_conf_symlink_rel_path.value: abs_path("/abs/lconf")},
        )

    # then:
    assert "cannot be absolute" in str(exc_info.value)
