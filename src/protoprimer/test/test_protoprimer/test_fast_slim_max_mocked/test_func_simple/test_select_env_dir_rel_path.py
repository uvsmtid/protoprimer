import pathlib

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _select_env_dir_rel_path,
    _SelectorFunc,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        _select_env_dir_rel_path.__name__,
    )


def _write_selector(
    tmp_path: pathlib.Path,
    code: str,
) -> str:
    # The real `import` is used (it cannot read a fake file system):
    selector_file_path = tmp_path / "env_selector.py"
    selector_file_path.write_text(code)
    return str(selector_file_path)


def test_returns_str_from_selector(tmp_path):
    # given:
    selector_file_abs_path = _write_selector(
        tmp_path,
        f"def {_SelectorFunc.select_env_dir_rel_path.value}():\n    return 'some/env'\n",
    )

    # when:
    result = _select_env_dir_rel_path(selector_file_abs_path)

    # then:
    assert result == "some/env"


def test_returns_none_from_selector(tmp_path):
    # given:
    selector_file_abs_path = _write_selector(
        tmp_path,
        f"def {_SelectorFunc.select_env_dir_rel_path.value}():\n    return None\n",
    )

    # when:
    result = _select_env_dir_rel_path(selector_file_abs_path)

    # then:
    assert result is None


def test_failure_when_selector_file_is_missing(tmp_path):
    # when:
    with pytest.raises(AssertionError) as exc_info:
        _select_env_dir_rel_path(str(tmp_path / "missing.py"))

    # then:
    assert "which does not exist" in str(exc_info.value)


def test_failure_when_selector_function_is_missing(tmp_path):
    # given:
    selector_file_abs_path = _write_selector(tmp_path, "x = 1\n")

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _select_env_dir_rel_path(selector_file_abs_path)

    # then:
    assert f"does not define `{_SelectorFunc.select_env_dir_rel_path.value}`" in str(exc_info.value)


@pytest.mark.parametrize("returned_value", ["5", "['a']", "b'bytes'"])
def test_failure_when_selector_returns_not_str(tmp_path, returned_value):
    # given:
    selector_file_abs_path = _write_selector(
        tmp_path,
        f"def {_SelectorFunc.select_env_dir_rel_path.value}():\n    return {returned_value}\n",
    )

    # when:
    with pytest.raises(AssertionError) as exc_info:
        _select_env_dir_rel_path(selector_file_abs_path)

    # then:
    assert "must return `str` or `None`" in str(exc_info.value)


def test_selector_exception_propagates(tmp_path):
    # given:
    selector_file_abs_path = _write_selector(
        tmp_path,
        f"def {_SelectorFunc.select_env_dir_rel_path.value}():\n    raise RuntimeError('selector failed')\n",
    )

    # when:
    with pytest.raises(RuntimeError) as exc_info:
        _select_env_dir_rel_path(selector_file_abs_path)

    # then:
    assert "selector failed" in str(exc_info.value)
