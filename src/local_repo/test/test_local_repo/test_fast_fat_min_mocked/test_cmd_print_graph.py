import os
import sys
from io import StringIO
from unittest.mock import patch

from local_repo import cmd_print_graph
from local_repo import graph_printer
from local_repo.cmd_print_graph import (
    custom_main,
)
from local_repo.graph_printer import StateMeta
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from protoprimer.primer_kernel import EnvState


graph_printer_file_name = os.path.basename(str(graph_printer.__file__))


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_print_graph.__name__)


def test_state_meta_matches_env_state():

    # given:

    env_state_names = [enum_item.name for enum_item in EnvState]
    state_meta_names = [enum_item.name for enum_item in StateMeta]

    # then:

    if env_state_names != state_meta_names:
        raise AssertionError("StateMeta should define enum item for every EnvState, in the same order, with the same name")


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch.object(
    sys,
    "argv",
    [graph_printer_file_name],
)
def test_print_dag_cmd_default(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch.object(
    sys,
    "argv",
    [
        graph_printer_file_name,
        "--format",
        "text",
    ],
)
def test_print_dag_cmd_text(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch.object(
    sys,
    "argv",
    [
        graph_printer_file_name,
        "--format",
        "mermaid",
    ],
)
def test_print_dag_cmd_mermaid(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch.object(
    sys,
    "argv",
    [
        graph_printer_file_name,
        "--layout",
        "flat",
    ],
)
def test_print_dag_cmd_layout_flat(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch.object(
    sys,
    "argv",
    [
        graph_printer_file_name,
        "--format",
        "mermaid",
        "--layout",
        "flat",
    ],
)
def test_print_dag_cmd_mermaid_flat_fail():

    # given:

    # when & then:

    try:
        custom_main()
    except ValueError as error_msg:
        expected_message = "Format `mermaid` requires layout `nested`"
        if expected_message not in str(error_msg):
            raise AssertionError(f"Expected `{expected_message}` in `{str(error_msg)}`")
    else:
        raise AssertionError(f"Expected `{ValueError.__name__}` was not raised")
