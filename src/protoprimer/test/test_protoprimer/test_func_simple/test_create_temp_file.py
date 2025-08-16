import tempfile
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import create_temp_file


def test_relationship():
    assert_test_module_name_embeds_str(
        create_temp_file.__name__,
    )


@patch(f"{tempfile.__name__}.NamedTemporaryFile")
def test_create_temp_file(mock_named_temporary_file):

    # when:

    create_temp_file()

    # then:

    mock_named_temporary_file.assert_called_once_with(
        mode="w+t",
        encoding="utf-8",
    )
