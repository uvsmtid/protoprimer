import os
import pathlib
import stat

from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_plain_proto_code,
    switch_to_ref_root_abs_path,
)
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    ExecOperation,
    SyntaxArg,
    generate_entry_script_content,
)


def test_relationship():
    assert_test_module_name_embeds_str(ExecOperation.op_wrap.value)


def _wrap_and_assert(
    tmp_path: pathlib.Path,
    entry_func: EntryFunc,
):
    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)
    proto_kernel_abs_path = create_plain_proto_code(ref_root_abs_path)

    entry_script_abs_path = ref_root_abs_path / "cmd" / "some_app"
    entry_script_abs_path.parent.mkdir(parents=True)

    main_func = "some_app:some_main"

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            ExecOperation.op_wrap.value,
            entry_func.value,
            SyntaxArg.arg_entry_script_path,
            str(entry_script_abs_path),
            SyntaxArg.arg_main_func,
            main_func,
        ]
    )

    # then:

    assert entry_script_abs_path.is_file()

    entry_script_stat = os.stat(entry_script_abs_path)
    assert entry_script_stat.st_mode & stat.S_IXUSR

    expected_content = generate_entry_script_content(
        entry_func.value,
        str(proto_kernel_abs_path),
        str(entry_script_abs_path),
        "some_app",
        "some_main",
    )
    assert entry_script_abs_path.read_text() == expected_content


def test_wrap_boot_env(tmp_path: pathlib.Path):

    assert_test_func_name_embeds_str(EntryFunc.func_boot_env.value)

    _wrap_and_assert(tmp_path, EntryFunc.func_boot_env)


def test_wrap_start_app(tmp_path: pathlib.Path):

    assert_test_func_name_embeds_str(EntryFunc.func_start_app.value)

    _wrap_and_assert(tmp_path, EntryFunc.func_start_app)
