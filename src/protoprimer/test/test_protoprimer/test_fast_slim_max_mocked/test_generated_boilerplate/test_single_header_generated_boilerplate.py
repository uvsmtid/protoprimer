"""
FT_56_85_65_41.generated_boilerplate.md
"""

import protoprimer.primer_kernel as pk_mod

from protoprimer.primer_kernel import (
    ConfConstGeneral,
    read_text_file,
    _replace_single_header_in_empty_lines,
    write_text_file,
)


def test_replace_single_header_in_empty_lines(fs):

    # given:

    input_content = (
        #
        "#!/usr/bin/env python3\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "import os\n"
    )
    input_path = "/test_input.py"
    output_path = "/test_output.py"
    fs.create_file(input_path, contents=input_content)

    # when:

    header_text = ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(pk_mod)
    result = _replace_single_header_in_empty_lines(
        input_text=read_text_file(input_path),
        boilerplate_text=header_text,
    )
    write_text_file(output_path, result)

    # then:

    expected_content = (
        #
        "#!/usr/bin/env python3\n"
        "################################################################################\n"
        "########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########\n"
        "################################################################################\n"
        "# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.\n"
        "# It is supposed to be versioned\n"
        "# (to be available in the target client repo on clone),\n"
        "# but it should not be linted\n"
        "# (as its content/style is governed by the source repo).\n"
        "################################################################################\n"
        "\n"
        "import os\n"
    )
    assert read_text_file(output_path) == expected_content
