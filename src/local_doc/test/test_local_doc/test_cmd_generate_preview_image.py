from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from local_doc import cmd_generate_preview_image
from local_test.repo_tree import change_to_known_repo_path

_png_signature = b"\x89PNG\r\n\x1a\n"

_shell_snippet_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="645" height="342" viewBox="0 0 645 342"></svg>'


def _create_ref_root(ref_root_path: Path) -> None:
    for svg_rel_path, svg_text in [
        (cmd_generate_preview_image.logo_svg_rel_path, '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"></svg>'),
        (cmd_generate_preview_image.shell_snippet_svg_rel_path, _shell_snippet_svg),
    ]:
        svg_abs_path = ref_root_path / svg_rel_path
        svg_abs_path.parent.mkdir(parents=True, exist_ok=True)
        svg_abs_path.write_text(svg_text)


def _list_png_chunk_types(png_path: Path) -> list[str]:
    png_bytes = png_path.read_bytes()
    chunk_types: list[str] = []
    chunk_offset = len(_png_signature)
    while chunk_offset < len(png_bytes):
        chunk_length = int.from_bytes(png_bytes[chunk_offset : chunk_offset + 4], "big")
        chunk_type = png_bytes[chunk_offset + 4 : chunk_offset + 8].decode()
        # Merge consecutive `IDAT` chunks (their number depends on the compressed size):
        if not chunk_types or chunk_types[-1] != chunk_type:
            chunk_types.append(chunk_type)
        # length + type + data + CRC:
        chunk_offset += 4 + 4 + chunk_length + 4
    return chunk_types


def test_arg_parser_defaults() -> None:
    # when:
    parsed_args = cmd_generate_preview_image.init_arg_parser().parse_args([])

    # then:
    assert parsed_args.dry_run is False


def test_arg_parser_dry_run() -> None:
    # when:
    parsed_args = cmd_generate_preview_image.init_arg_parser().parse_args(["--dry_run"])

    # then:
    assert parsed_args.dry_run is True


def test_arg_parser_help_mentions_preview_image(capsys) -> None:
    # when:
    with pytest.raises(SystemExit) as exit_info:
        cmd_generate_preview_image.init_arg_parser().parse_args(["--help"])

    # then:
    assert exit_info.value.code == 0
    assert "preview image" in capsys.readouterr().out


def test_layout_fills_canvas_without_gap() -> None:
    # then:
    assert cmd_generate_preview_image.logo_size_px + cmd_generate_preview_image.shell_width_px == cmd_generate_preview_image.canvas_width_px
    assert 0 <= cmd_generate_preview_image.top_offset_px
    assert cmd_generate_preview_image.logo_size_px <= cmd_generate_preview_image.canvas_height_px


def test_parse_svg_width() -> None:
    # then:
    assert cmd_generate_preview_image.parse_svg_width(_shell_snippet_svg) == 645


def test_parse_svg_width_missing_raises() -> None:
    # then:
    with pytest.raises(ValueError):
        cmd_generate_preview_image.parse_svg_width('<svg viewBox="0 0 16 16"></svg>')


def test_build_commands(tmp_path: Path) -> None:
    # given:
    shell_snippet_svg_path = tmp_path / "shell_snippet.svg"
    shell_snippet_svg_path.write_text(_shell_snippet_svg)

    # when:
    command_args_list = cmd_generate_preview_image.build_commands(
        logo_svg_abs_path="/in/logo.svg",
        logo_png_abs_path="/tmp/logo.png",
        logo_scaled_png_abs_path="/tmp/logo_scaled.png",
        shell_snippet_svg_abs_path=str(shell_snippet_svg_path),
        shell_snippet_png_abs_path="/tmp/shell_snippet.png",
        preview_png_abs_path="/out/preview.png",
    )

    # then:
    assert command_args_list[0] == [
        "magick",
        "-background",
        "none",
        "-density",
        "96",
        "/in/logo.svg",
        "/tmp/logo.png",
    ]
    assert command_args_list[1] == [
        "magick",
        "/tmp/logo.png",
        "-filter",
        "point",
        "-resize",
        "2600%",
        "/tmp/logo_scaled.png",
    ]
    assert command_args_list[2] == [
        "magick",
        "-background",
        "none",
        "-density",
        str(96 * 784 / 645),
        str(shell_snippet_svg_path),
        "-resize",
        "784x",
        "/tmp/shell_snippet.png",
    ]
    assert command_args_list[3] == [
        "magick",
        "-size",
        "1200x630",
        "xc:black",
        "/tmp/logo_scaled.png",
        "-geometry",
        "+0+107",
        "-composite",
        "/tmp/shell_snippet.png",
        "-geometry",
        "+416+107",
        "-composite",
        "-strip",
        "-depth",
        "8",
        "PNG24:/out/preview.png",
    ]


def test_generate_preview_image_file_missing_input_raises(tmp_path: Path) -> None:
    # given:
    # (empty ref root)

    # then:
    with pytest.raises(FileNotFoundError):
        cmd_generate_preview_image.generate_preview_image_file(
            ref_root_abs_path=str(tmp_path),
            dry_run=False,
        )


@patch("shutil.which", return_value=None)
def test_generate_preview_image_file_missing_magick_raises(mock_which: MagicMock, tmp_path: Path) -> None:
    # given:
    _create_ref_root(tmp_path)

    # then:
    with pytest.raises(RuntimeError):
        cmd_generate_preview_image.generate_preview_image_file(
            ref_root_abs_path=str(tmp_path),
            dry_run=False,
        )


@patch("subprocess.run")
@patch("shutil.which", return_value="/usr/bin/magick")
def test_generate_preview_image_file_runs_commands_in_order(
    mock_which: MagicMock,
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    # given:
    _create_ref_root(tmp_path)

    # when:
    cmd_generate_preview_image.generate_preview_image_file(
        ref_root_abs_path=str(tmp_path),
        dry_run=False,
    )

    # then:
    assert mock_run.call_count == 4
    # (`call.args` and `call.kwargs` exist only since `python` 3.8, so unpack the call as a tuple)
    called_args_list = [call_args[0] for call_args, _ in mock_run.call_args_list]
    assert all(called_args[0] == "magick" for called_args in called_args_list)
    # The first command rasterizes the logo from `ref_root`, the last one writes the preview into `ref_root`:
    assert str(tmp_path / cmd_generate_preview_image.logo_svg_rel_path) in called_args_list[0]
    assert called_args_list[3][-1] == f"PNG24:{tmp_path / cmd_generate_preview_image.preview_png_rel_path}"
    assert all(call_kwargs == {"check": True} for _, call_kwargs in mock_run.call_args_list)


@patch("subprocess.run")
def test_generate_preview_image_file_dry_run_runs_nothing(mock_run: MagicMock, tmp_path: Path) -> None:
    # given:
    _create_ref_root(tmp_path)

    # when:
    cmd_generate_preview_image.generate_preview_image_file(
        ref_root_abs_path=str(tmp_path),
        dry_run=True,
    )

    # then:
    mock_run.assert_not_called()
    assert not (tmp_path / cmd_generate_preview_image.preview_png_rel_path).exists()


@patch("sys.argv", ["generate_preview_image", "--dry_run"])
@patch(f"{cmd_generate_preview_image.__name__}.generate_preview_image_file")
@patch(f"{cmd_generate_preview_image.__name__}.configure_script")
def test_generate_preview_image_uses_ref_root(
    mock_configure_script: MagicMock,
    mock_generate_preview_image_file: MagicMock,
) -> None:
    # given:
    mock_configure_script.return_value = {
        cmd_generate_preview_image._EnvState.state_ref_root_dir_abs_path_inited.name: "/fake_repo",
    }

    # when:
    cmd_generate_preview_image.generate_preview_image()

    # then:
    mock_generate_preview_image_file.assert_called_once_with(
        ref_root_abs_path="/fake_repo",
        dry_run=True,
    )


@pytest.mark.skipif(
    shutil.which("magick") is None,
    reason="ImageMagick (`magick`) is not installed",
)
def test_generate_preview_image_file_real_magick(tmp_path: Path) -> None:
    # given:
    with change_to_known_repo_path():
        real_ref_root_path = Path(os.getcwd())
    for svg_rel_path in [
        cmd_generate_preview_image.logo_svg_rel_path,
        cmd_generate_preview_image.shell_snippet_svg_rel_path,
    ]:
        copied_svg_path = tmp_path / svg_rel_path
        copied_svg_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(real_ref_root_path / svg_rel_path, copied_svg_path)

    # when:
    cmd_generate_preview_image.generate_preview_image_file(
        ref_root_abs_path=str(tmp_path),
        dry_run=False,
    )

    # then:
    preview_png_path = tmp_path / cmd_generate_preview_image.preview_png_rel_path
    identify_output = subprocess.run(
        [
            "magick",
            "identify",
            "-format",
            "%wx%h",
            str(preview_png_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert identify_output == "1200x630"

    # No metadata chunks (e.g. timestamps): the same bytes on each run (stable diff in git):
    assert _list_png_chunk_types(preview_png_path) == [
        "IHDR",
        "IDAT",
        "IEND",
    ]
