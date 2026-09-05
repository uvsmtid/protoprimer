from __future__ import annotations

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import parse_python_version_prefix


def test_relationship():
    assert_test_module_name_embeds_str(
        parse_python_version_prefix.__name__,
    )


@pytest.mark.parametrize(
    "version_str, expected_tuple",
    [
        ("3", (3,)),
        ("3.10", (3, 10)),
        ("3.10.1", (3, 10, 1)),
        ("3.10.1-beta", (3, 10, 1)),
        ("3.10b5", (3, 10)),
        ("3.10.1.2", (3, 10, 1)),
    ],
)
def test_parse_python_version_prefix(version_str, expected_tuple):
    # when:
    parsed_version_prefix = parse_python_version_prefix(version_str)
    # then:
    assert parsed_version_prefix == expected_tuple
