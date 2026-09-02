from __future__ import annotations

from unittest.mock import patch
from xml.dom.minidom import parseString

import pytest

from local_doc import cmd_render_shell

_reduced_shell_script = 'msg=hi\necho "$msg"'

# A minimal SVG in the shape `generate` emits, squashed onto one line:
_reduced_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="20" viewBox="0 0 30 20" role="img" aria-label="shell snippet"><rect x="0.5" y="0.5" width="29" height="19" rx="6" fill="#000000" stroke="#000000"/><g transform="translate(16,12)"><g font-family="monospace" font-size="14px"><text x="0" y="14"><tspan fill="#e6edf3">hi</tspan><tspan fill="#79c0ff">there</tspan></text></g></g></svg>'


def test_generate_sub_command_pretty_prints_svg(fs, capsys) -> None:
    # given:
    fs.create_file("/fake/snippet.sh", contents=_reduced_shell_script + "\n")

    # when:
    with patch("sys.argv", ["render_shell", "generate", "/fake/snippet.sh"]):
        cmd_render_shell.render_shell()

    # then:
    generated_svg = capsys.readouterr().out
    parseString(generated_svg)
    assert generated_svg.startswith("<svg\n")
    assert '\n  xmlns="http://www.w3.org/2000/svg"\n' in generated_svg
    assert "\n  <rect\n" in generated_svg
    assert '\n    fill="#000000"\n' in generated_svg
    # One `<text>` per script line, plus the trailing empty `<text>` `pygments` adds:
    assert generated_svg.count("\n      <text\n") == 3
    assert ">msg</tspan>" in generated_svg
    assert ">echo</tspan>" in generated_svg
    # Every `<tspan>` split out with an absolute `x`, and `xml:space` dropped:
    assert "\n        <tspan\n" in generated_svg
    assert '\n          x="0.0"\n' in generated_svg
    assert '\n          fill="#79c0ff"\n' in generated_svg
    assert "xml:space" not in generated_svg


def test_reformat_sub_command_pretty_prints_svg(fs, capsys) -> None:
    # given:
    fs.create_file("/fake/messy.svg", contents=_reduced_svg)

    # when:
    with patch("sys.argv", ["render_shell", "reformat", "/fake/messy.svg"]):
        cmd_render_shell.render_shell()

    # then:
    reformatted_svg = capsys.readouterr().out
    parseString(reformatted_svg)
    assert reformatted_svg.startswith("<svg\n")
    assert '\n  aria-label="shell snippet"\n' in reformatted_svg
    assert '\n          fill="#e6edf3"\n' in reformatted_svg
    assert '\n          fill="#79c0ff"\n' in reformatted_svg
    # `<tspan>` `x` is recomputed from the column width (`len("hi") * 8.4`):
    assert '\n          x="0.0"\n' in reformatted_svg
    assert '\n          x="16.8"\n' in reformatted_svg
    assert "xml:space" not in reformatted_svg


def test_reformat_svg_is_idempotent() -> None:
    # given:
    reformatted_once = cmd_render_shell.reformat_svg(_reduced_svg)

    # when:
    reformatted_twice = cmd_render_shell.reformat_svg(reformatted_once)

    # then:
    assert reformatted_twice == reformatted_once


def test_generated_svg_survives_reformat_unchanged() -> None:
    # given:
    generated_svg = cmd_render_shell.generate_svg(_reduced_shell_script, "github-dark")

    # when:
    reformatted_svg = cmd_render_shell.reformat_svg(generated_svg)

    # then:
    assert reformatted_svg == generated_svg


def test_reformat_sub_command_rejects_unrelated_svg(fs) -> None:
    # given:
    fs.create_file(
        "/fake/not_a_snippet.svg",
        contents='<svg xmlns="http://www.w3.org/2000/svg"><circle r="1"/></svg>',
    )

    # when:
    with patch("sys.argv", ["render_shell", "reformat", "/fake/not_a_snippet.svg"]):
        # then:
        with pytest.raises(RuntimeError):
            cmd_render_shell.render_shell()


def test_lint_svg_returns_zero_for_already_pretty_svg(fs) -> None:
    # given:
    pretty_svg = cmd_render_shell.reformat_svg(_reduced_svg)
    fs.create_file("/fake/pretty.svg", contents=pretty_svg)

    # when:
    exit_code = cmd_render_shell.lint_svg("/fake/pretty.svg")

    # then:
    assert exit_code == 0


def test_lint_svg_returns_one_and_prints_diff_for_messy_svg(fs, capsys) -> None:
    # given:
    fs.create_file("/fake/messy.svg", contents=_reduced_svg)

    # when:
    exit_code = cmd_render_shell.lint_svg("/fake/messy.svg")

    # then:
    assert exit_code == 1
    printed_diff = capsys.readouterr().err
    assert "--- /fake/messy.svg" in printed_diff
    assert "+++ /fake/messy.svg (reformatted)" in printed_diff
    assert "not pretty-printed -- run: cmd/render_shell reformat /fake/messy.svg" in printed_diff


def test_lint_sub_command_exits_zero_for_already_pretty_svg(fs) -> None:
    # given:
    pretty_svg = cmd_render_shell.reformat_svg(_reduced_svg)
    fs.create_file("/fake/pretty.svg", contents=pretty_svg)

    # when:
    with patch("sys.argv", ["render_shell", "lint", "/fake/pretty.svg"]):
        with pytest.raises(SystemExit) as raised_exit:
            cmd_render_shell.render_shell()

    # then:
    assert raised_exit.value.code == 0


def test_lint_sub_command_exits_nonzero_for_messy_svg(fs) -> None:
    # given:
    fs.create_file("/fake/messy.svg", contents=_reduced_svg)

    # when:
    with patch("sys.argv", ["render_shell", "lint", "/fake/messy.svg"]):
        with pytest.raises(SystemExit) as raised_exit:
            cmd_render_shell.render_shell()

    # then:
    assert raised_exit.value.code == 1
