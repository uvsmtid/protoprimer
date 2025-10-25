import os
import pathlib
import sys
from unittest.mock import patch, MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

import protoprimer
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    main,
)


class ExecCalled(Exception):
    pass


def mock_execv(*args, **kwargs):
    raise ExecCalled(args, kwargs)


def mock_execve(*args, **kwargs):
    raise ExecCalled(args, kwargs)


@pytest.mark.skip("incomplete & experimental")
@patch("os.execv", side_effect=mock_execv)
@patch("os.execve", side_effect=mock_execve)
@patch("subprocess.check_call", return_value=0)
@patch("venv.create")
@patch("shutil.move")
def test_prime_with_mocked_execv(
    mock_execv_call,
    mock_execve_call,
    mock_check_call,
    mock_venv_create,
    mock_shutil_move,
    fs: FakeFilesystem,
):

    # given:

    fs.add_real_file(protoprimer.primer_kernel.__file__)

    tmp_dir_abs_path: str = fs.create_dir("/project_dir").path
    tmp_path: pathlib.Path = pathlib.Path(tmp_dir_abs_path)

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===
    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===
    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # ===
    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===
    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    # ===
    # when:
    argv = [
        str(proto_code_dir_abs_path / ConfConstGeneral.default_proto_code_basename),
    ]
    for _ in range(10):
        try:
            with patch.object(
                sys,
                "argv",
                argv,
            ):
                main()
            break
        except ExecCalled as e:
            args, kwargs = e.args
            if "argv" in kwargs:
                argv = kwargs["argv"]
            else:
                argv = args[1]
            if isinstance(argv, tuple):
                argv = list(argv)

    # then:
    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

    conf_primer_file = (
        ref_root_abs_path
        / ConfConstGeneral.name_proto_code
        / ConfConstInput.default_file_basename_conf_primer
    )
    conf_client_file = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_file_rel_path
    )
    conf_env_file = ref_root_abs_path / ConfConstClient.default_env_conf_file_rel_path

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
