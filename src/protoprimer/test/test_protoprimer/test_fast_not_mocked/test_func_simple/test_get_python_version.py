from __future__ import annotations

import sys

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import get_python_version


def test_relationship():
    assert_test_module_name_embeds_str(
        get_python_version.__name__,
    )


def test_get_python_version():

    # given:

    expected_version_tuple = sys.version_info[:3]

    # when:

    python_version: tuple[int, int, int] = get_python_version(
        path_to_python=sys.executable
    )

    # then:

    assert python_version == expected_version_tuple
