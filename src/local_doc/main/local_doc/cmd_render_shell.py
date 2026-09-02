from __future__ import annotations

import argparse
import logging
import re
import sys

from pygments import highlight
from pygments.formatters import SvgFormatter
from pygments.lexers import BashLexer

logger = logging.getLogger(__name__)

# `SvgFormatter` emits one `<text>` per line stepped by this many px at its
# default font size, and a monospace glyph advances by roughly `char_width`:
line_step_px = 19
char_width_px = 8.4

# Padding between the code and the rounded frame:
pad_x_px = 16
pad_top_px = 12
pad_bottom_px = 12

background_color = "#0d1117"
border_color = "#30363d"

_svg_group_re = re.compile(r'<g font-family="monospace".*?</g>', re.DOTALL)


def render_shell() -> None:
    """
    Main func to render a shell script as a self-contained, syntax-highlighted SVG on stdout.

    `pygments` produces a bare `<g>` of colored `<tspan>` runs; this wraps it
    in an `<svg>` with an explicit `viewBox` and a rounded dark background so
    it renders as a code block when referenced via `<img>` in Markdown.
    """

    arg_parser_instance = init_arg_parser()
    parsed_arguments = arg_parser_instance.parse_args()

    with open(parsed_arguments.shell_script) as shell_script_file:
        shell_script_text = shell_script_file.read().rstrip("\n")

    sys.stdout.write(
        render_svg(
            shell_script_text,
            parsed_arguments.color_style,
        )
    )


def init_arg_parser():
    """
    Initializes and configures the argument parser for the script.

    Returns:
        An instance of `argparse.ArgumentParser`.
    """
    arg_parser_instance = argparse.ArgumentParser(
        description="Render a shell script as a self-contained, syntax-highlighted SVG on stdout.",
    )
    arg_parser_instance.add_argument(
        "shell_script",
        type=str,
        help="Path to the shell script to render.",
    )
    arg_parser_instance.add_argument(
        "--color_style",
        "-s",
        dest="color_style",
        type=str,
        default="github-dark",
        help="`pygments` color style name (default: `github-dark`).",
    )
    return arg_parser_instance


def render_svg(
    shell_script_text: str,
    style_name: str,
) -> str:
    """
    Wraps the `pygments` SVG fragment for `shell_script_text` into a framed `<svg>` document.
    """
    highlighted_svg = highlight(
        shell_script_text,
        BashLexer(),
        SvgFormatter(style=style_name),
    )

    group_match = _svg_group_re.search(highlighted_svg)
    if group_match is None:
        raise RuntimeError("`pygments` `SvgFormatter` produced no `<g>` element")
    svg_group = group_match.group(0)

    script_lines = shell_script_text.splitlines()
    column_count = max((len(script_line) for script_line in script_lines), default=0)

    svg_width = round(pad_x_px * 2 + column_count * char_width_px)
    svg_height = round(pad_top_px + 14 + (len(script_lines) - 1) * line_step_px + pad_bottom_px)

    # The trailing "" adds the final newline; the trailing comma keeps `black` from
    # collapsing this list onto a single line (the hook runs with `--line-length 999`).
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" role="img" aria-label="shell snippet">',
        f'  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="6" fill="{background_color}" stroke="{border_color}"/>',
        f'  <g transform="translate({pad_x_px},{pad_top_px})">',
        f"  {svg_group}",
        "  </g>",
        "</svg>",
        "",
    ]
    return "\n".join(svg_lines)


if __name__ == "__main__":
    render_shell()
