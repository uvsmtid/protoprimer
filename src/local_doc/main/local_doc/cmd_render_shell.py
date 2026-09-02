from __future__ import annotations

import argparse
import difflib
import logging
import re
import sys

from pygments import highlight
from pygments.formatters import SvgFormatter
from pygments.lexers import BashLexer

logger = logging.getLogger(__name__)

# Vertical distance between two `<text>` lines `pygments` `SvgFormatter` emits:
line_step_px = 19
# Advance of one monospace glyph, used to position each `<tspan>`'s absolute `x`:
char_width_px = 8.4

# Padding between the code and the rounded frame:
pad_x_px = 16
pad_top_px = 12
pad_bottom_px = 12

# Black, to match the logo (`doc/_static/protoprimer.logo.svg`):
background_color = "#000000"
border_color = "#000000"

# Two-space indent step for the pretty-printed SVG:
xml_indent = "  "

_xml_prolog_re = re.compile(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", re.IGNORECASE)
_svg_open_re = re.compile(r"<svg\b([^>]*)>")
_rect_re = re.compile(r"<rect\b([^>]*?)\s*/?>")
_outer_group_re = re.compile(r"<g\b([^>]*?\btransform=[^>]*?)>")
_inner_group_re = re.compile(r'<g (font-family="[^"]*"[^>]*?)>(.*?)</g>', re.DOTALL)
_text_element_re = re.compile(r"<text\b[^>]*>.*?</text>", re.DOTALL)
_tspan_re = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.DOTALL)
_attribute_re = re.compile(r'\S+="[^"]*"')
_baseline_y_re = re.compile(r'\by="(-?\d+(?:\.\d+)?)"')
_entity_re = re.compile(r"&(?:#\d+|#x[0-9A-Fa-f]+|[A-Za-z]+);")


def render_shell() -> None:
    """
    Main func to render or reformat a self-contained, syntax-highlighted shell-snippet SVG.
    """

    parsed_arguments = init_arg_parser().parse_args()

    if parsed_arguments.command == "generate":
        with open(parsed_arguments.shell_script) as shell_script_file:
            output_svg = generate_svg(
                shell_script_file.read().rstrip("\n"),
                parsed_arguments.color_style,
            )
    elif parsed_arguments.command == "reformat":
        with open(parsed_arguments.svg_file) as svg_file:
            output_svg = reformat_svg(svg_file.read())
    elif parsed_arguments.command == "lint":
        sys.exit(lint_svg(parsed_arguments.svg_file))
    else:
        raise AssertionError(parsed_arguments.command)

    sys.stdout.write(output_svg)


def init_arg_parser():
    arg_parser_instance = argparse.ArgumentParser(
        description="Render or reformat a self-contained, syntax-highlighted shell-snippet SVG on stdout.",
    )
    sub_parsers = arg_parser_instance.add_subparsers(dest="command", required=True)

    generate_parser = sub_parsers.add_parser(
        "generate",
        help="Generate an SVG from a shell script.",
    )
    generate_parser.add_argument(
        "shell_script",
        type=str,
        help="Path to the shell script to render.",
    )
    generate_parser.add_argument(
        "--color_style",
        "-s",
        dest="color_style",
        type=str,
        default="github-dark",
        help="`pygments` color style name (default: `github-dark`).",
    )

    reformat_parser = sub_parsers.add_parser(
        "reformat",
        help="Reformat an existing shell-snippet SVG (as produced by `generate`).",
    )
    reformat_parser.add_argument(
        "svg_file",
        type=str,
        help="Path to the SVG file to reformat.",
    )

    lint_parser = sub_parsers.add_parser(
        "lint",
        help="Check that a shell-snippet SVG is already pretty-printed (exits non-zero otherwise).",
    )
    lint_parser.add_argument(
        "svg_file",
        type=str,
        help="Path to the SVG file to check.",
    )

    return arg_parser_instance


def generate_svg(
    shell_script_text: str,
    style_name: str,
) -> str:
    """
    Wraps the `pygments` SVG fragment for `shell_script_text` into a framed, pretty-printed `<svg>` document.
    """
    highlighted_svg = highlight(
        shell_script_text,
        BashLexer(),
        SvgFormatter(style=style_name),
    )

    inner_group_match = _inner_group_re.search(highlighted_svg)
    if inner_group_match is None:
        raise RuntimeError("`pygments` `SvgFormatter` produced no `<g>` element")
    inner_group_attributes = _attribute_re.findall(inner_group_match.group(1))
    text_elements = _text_element_re.findall(inner_group_match.group(2))

    script_lines = shell_script_text.splitlines()
    column_count = max((len(script_line) for script_line in script_lines), default=0)

    svg_width = round(pad_x_px * 2 + column_count * char_width_px)
    svg_height = round(pad_top_px + 14 + (len(script_lines) - 1) * line_step_px + pad_bottom_px)

    svg_attributes = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'width="{svg_width}"',
        f'height="{svg_height}"',
        f'viewBox="0 0 {svg_width} {svg_height}"',
        'role="img"',
        'aria-label="shell snippet"',
    ]
    rect_attributes = [
        'x="0.5"',
        'y="0.5"',
        f'width="{svg_width - 1}"',
        f'height="{svg_height - 1}"',
        'rx="6"',
        f'fill="{background_color}"',
        f'stroke="{border_color}"',
    ]
    outer_group_attributes = [
        f'transform="translate({pad_x_px},{pad_top_px})"',
    ]

    return _emit_svg(
        svg_attributes,
        rect_attributes,
        outer_group_attributes,
        inner_group_attributes,
        text_elements,
    )


def reformat_svg(svg_source: str) -> str:
    """
    Collapses an existing shell-snippet SVG to a single line, then re-emits it through `_emit_svg`.
    """
    minified_svg = _xml_prolog_re.sub("", svg_source)
    minified_svg = re.sub(r"\s+", " ", minified_svg).strip()
    minified_svg = re.sub(r">\s*<", "><", minified_svg)
    minified_svg = minified_svg.replace(" >", ">").replace(" />", "/>")

    svg_open_match = _svg_open_re.search(minified_svg)
    rect_match = _rect_re.search(minified_svg)
    outer_group_match = _outer_group_re.search(minified_svg)
    inner_group_match = _inner_group_re.search(minified_svg)
    if not (svg_open_match and rect_match and outer_group_match and inner_group_match):
        raise RuntimeError("input does not look like a shell-snippet SVG produced by `generate`")

    return _emit_svg(
        _attribute_re.findall(svg_open_match.group(1)),
        _attribute_re.findall(rect_match.group(1)),
        _attribute_re.findall(outer_group_match.group(1)),
        _attribute_re.findall(inner_group_match.group(1)),
        _text_element_re.findall(inner_group_match.group(2)),
    )


def lint_svg(svg_path: str) -> int:
    """
    Re-runs `reformat_svg` over `svg_path` and diffs the result against the file on disk.
    """
    with open(svg_path) as svg_file:
        original_svg = svg_file.read()

    reformatted_svg = reformat_svg(original_svg)

    if reformatted_svg == original_svg:
        return 0

    diff_lines = difflib.unified_diff(
        original_svg.splitlines(keepends=True),
        reformatted_svg.splitlines(keepends=True),
        fromfile=svg_path,
        tofile=f"{svg_path} (reformatted)",
    )
    sys.stderr.writelines(diff_lines)
    sys.stderr.write(f"\n{svg_path} is not pretty-printed -- run: cmd/render_shell reformat {svg_path}\n")
    return 1


def _emit_svg(
    svg_attributes: list[str],
    rect_attributes: list[str],
    outer_group_attributes: list[str],
    inner_group_attributes: list[str],
    text_elements: list[str],
) -> str:
    """
    Pretty-prints the given attribute lists and `<text>` runs into a framed `<svg>` document.
    """
    output_lines: list[str] = []
    output_lines.append("<svg")
    output_lines.extend(f"{xml_indent}{attribute}" for attribute in svg_attributes)
    output_lines.append(">")
    output_lines.append(f"{xml_indent}<rect")
    output_lines.extend(f"{xml_indent * 2}{attribute}" for attribute in rect_attributes)
    output_lines.append(f"{xml_indent}/>")
    output_lines.append(f"{xml_indent}<g")
    output_lines.extend(f"{xml_indent * 2}{attribute}" for attribute in outer_group_attributes)
    output_lines.append(f"{xml_indent}>")
    output_lines.append(f"{xml_indent * 2}<g")
    output_lines.extend(f"{xml_indent * 3}{attribute}" for attribute in inner_group_attributes)
    output_lines.append(f"{xml_indent * 2}>")
    for text_element in text_elements:
        output_lines.extend(_format_text_element(text_element, xml_indent * 3))
    output_lines.append(f"{xml_indent * 2}</g>")
    output_lines.append(f"{xml_indent}</g>")
    output_lines.append("</svg>")
    output_lines.append("")
    return "\n".join(output_lines)


def _format_text_element(text_element: str, base_indent: str) -> list[str]:
    """
    Splits one `<text>` run into fully indented lines with
    *   one `<tspan>` per line
    *   one attribute per line
    each `<tspan>` carrying a freshly computed absolute `x`
    (any `x`/`y` already on the input `<tspan>` is dropped).
    """
    baseline_y_match = _baseline_y_re.search(text_element)
    baseline_y = baseline_y_match.group(1) if baseline_y_match else "0"

    tspans_markup = text_element[text_element.index(">") + 1 : text_element.rindex("</text>")]

    formatted_lines = [
        f"{base_indent}<text",
        f'{base_indent}{xml_indent}x="0"',
        f'{base_indent}{xml_indent}y="{baseline_y}"',
        f"{base_indent}>",
    ]
    start_column = 0
    for tspan_attributes_text, tspan_content in _tspan_re.findall(tspans_markup):
        formatted_lines.append(f"{base_indent}{xml_indent}<tspan")
        formatted_lines.append(f'{base_indent}{xml_indent * 2}x="{round(start_column * char_width_px, 1)}"')
        formatted_lines.append(f'{base_indent}{xml_indent * 2}y="{baseline_y}"')
        for tspan_attribute in _attribute_re.findall(tspan_attributes_text):
            if tspan_attribute.startswith(("x=", "y=")):
                continue
            formatted_lines.append(f"{base_indent}{xml_indent * 2}{tspan_attribute}")
        formatted_lines.append(f"{base_indent}{xml_indent}>{tspan_content}</tspan>")
        start_column += len(_entity_re.sub(".", tspan_content))
    formatted_lines.append(f"{base_indent}</text>")
    return formatted_lines


if __name__ == "__main__":
    render_shell()
