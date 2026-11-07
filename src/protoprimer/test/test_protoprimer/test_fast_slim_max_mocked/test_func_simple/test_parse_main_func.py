import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _ConfConstGeneral,
    _parse_main_func,
)


def test_relationship():
    assert_test_module_name_embeds_str(_parse_main_func.__name__)


def test_valid_module_func():
    assert _parse_main_func("my_module:my_func", allow_default_proto_main=False) == (
        "my_module",
        "my_func",
    )


def test_splits_only_on_first_separator():
    assert _parse_main_func("my_module:my_sub:my_func", allow_default_proto_main=False) == (
        "my_module",
        "my_sub:my_func",
    )


def test_empty_main_func_allowed():
    assert _parse_main_func(_ConfConstGeneral.default_proto_main, allow_default_proto_main=True) == (
        None,
        None,
    )


def test_empty_main_func_rejected():
    with pytest.raises(ValueError):
        _parse_main_func(_ConfConstGeneral.default_proto_main, allow_default_proto_main=False)


def test_missing_separator_rejected():
    with pytest.raises(ValueError):
        _parse_main_func("invalid_format", allow_default_proto_main=False)
