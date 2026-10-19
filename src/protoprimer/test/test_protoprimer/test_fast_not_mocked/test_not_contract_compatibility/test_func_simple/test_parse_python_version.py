from __future__ import annotations

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import parse_python_version


def test_relationship():
    assert_test_module_name_embeds_str(
        parse_python_version.__name__,
    )


@pytest.mark.parametrize(
    "version_str, expected_tuple",
    [
        ("0", (0, 0, 0)),
        ("3.10", (3, 10, 0)),
        ("3.10.1", (3, 10, 1)),
        ("3.10.1-beta", (3, 10, 1)),
        ("3.10.1-beta.2", (3, 10, 1)),
        ("3", (3, 0, 0)),
        ("3.10b5", (3, 10, 0)),
        ("3.8.10", (3, 8, 10)),
        ("3.12.0a1", (3, 12, 0)),
    ],
)
def test_parse_python_version(version_str, expected_tuple):
    # when:
    parsed_version = parse_python_version(version_str)
    # then:
    assert parsed_version == expected_tuple
