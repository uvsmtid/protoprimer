# Generate the social preview image (`og:image`) out of the logo and the shell snippet (both SVG):
# ./cmd/generate_preview_image -h
# ./cmd/generate_preview_image --dry_run

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

from metaprimer.script_lib import configure_script
from protoprimer.primer_kernel import EnvState

logger = logging.getLogger(__name__)

# Relative to `ref_root`:
logo_svg_rel_path = "doc/_static/protoprimer.logo.svg"
shell_snippet_svg_rel_path = "doc/_static/shell_snippet.svg"
preview_png_rel_path = "doc/_static/protoprimer.preview.1200x630.png"

magick_executable = "magick"

canvas_width_px = 1200
canvas_height_px = 630

# The logo is a 16x16 pixel art: only an integer scale (no interpolation) keeps it sharp:
logo_cell_count = 16
logo_scale = 26
logo_size_px = logo_cell_count * logo_scale

# The shell snippet takes the rest of the width (the logo and the snippet are flush):
shell_width_px = canvas_width_px - logo_size_px

# Both are centered vertically:
top_offset_px = (canvas_height_px - logo_size_px) // 2

# Default `ImageMagick` density to rasterize SVG with a 1:1 pixel size:
svg_density_dpi = 96

_svg_width_re = re.compile(r"<svg\b[^>]*?\swidth=\"(\d+(?:\.\d+)?)\"")


def generate_preview_image() -> None:
    """
    Main func to compose the logo and the shell snippet into the preview image.
    """

    parsed_arguments = init_arg_parser().parse_args()

    derived_data = configure_script(script_basename=os.path.basename(sys.argv[0]))
    ref_root_abs_path: str = derived_data[EnvState.state_ref_root_dir_abs_path_inited.name]

    generate_preview_image_file(
        ref_root_abs_path=ref_root_abs_path,
        dry_run=parsed_arguments.dry_run,
    )


def init_arg_parser():
    arg_parser_instance = argparse.ArgumentParser(
        description="Generate the preview image (logo + shell snippet) for social link previews.",
    )
    arg_parser_instance.add_argument(
        "--dry_run",
        action="store_true",
        help="Print the commands instead of running them.",
    )
    return arg_parser_instance


def generate_preview_image_file(
    ref_root_abs_path: str,
    dry_run: bool,
) -> None:
    logo_svg_abs_path = os.path.join(
        ref_root_abs_path,
        logo_svg_rel_path,
    )
    shell_snippet_svg_abs_path = os.path.join(
        ref_root_abs_path,
        shell_snippet_svg_rel_path,
    )
    preview_png_abs_path = os.path.join(
        ref_root_abs_path,
        preview_png_rel_path,
    )

    for input_abs_path in [
        logo_svg_abs_path,
        shell_snippet_svg_abs_path,
    ]:
        if not os.path.isfile(input_abs_path):
            raise FileNotFoundError(f"input file not found: {input_abs_path}")

    if not dry_run and shutil.which(magick_executable) is None:
        raise RuntimeError(f"`{magick_executable}` (ImageMagick) not found in `PATH`")

    with tempfile.TemporaryDirectory() as temp_dir_abs_path:
        logo_png_abs_path = os.path.join(temp_dir_abs_path, "logo.png")
        logo_scaled_png_abs_path = os.path.join(temp_dir_abs_path, "logo_scaled.png")
        shell_snippet_png_abs_path = os.path.join(temp_dir_abs_path, "shell_snippet.png")

        command_args_list = build_commands(
            logo_svg_abs_path=logo_svg_abs_path,
            logo_png_abs_path=logo_png_abs_path,
            logo_scaled_png_abs_path=logo_scaled_png_abs_path,
            shell_snippet_svg_abs_path=shell_snippet_svg_abs_path,
            shell_snippet_png_abs_path=shell_snippet_png_abs_path,
            preview_png_abs_path=preview_png_abs_path,
        )

        for command_args in command_args_list:
            logger.info(f"running command: {' '.join(command_args)}")
            if not dry_run:
                subprocess.run(
                    command_args,
                    check=True,
                )

    if not dry_run:
        logger.info(f"generated: {preview_png_abs_path}")


def build_commands(
    logo_svg_abs_path: str,
    logo_png_abs_path: str,
    logo_scaled_png_abs_path: str,
    shell_snippet_svg_abs_path: str,
    shell_snippet_png_abs_path: str,
    preview_png_abs_path: str,
) -> list[list[str]]:
    with open(shell_snippet_svg_abs_path) as shell_snippet_svg_file:
        shell_snippet_svg_width_px = parse_svg_width(shell_snippet_svg_file.read())

    # Rasterize the shell snippet directly at the target width (no bitmap upscaling):
    shell_snippet_density_dpi = svg_density_dpi * shell_width_px / shell_snippet_svg_width_px

    return [
        # 1. Rasterize the logo at 1:1 (one pixel per logo cell):
        [
            magick_executable,
            "-background",
            "none",
            "-density",
            str(svg_density_dpi),
            logo_svg_abs_path,
            logo_png_abs_path,
        ],
        # 2. Scale the logo by an integer factor without interpolation:
        [
            magick_executable,
            logo_png_abs_path,
            "-filter",
            "point",
            "-resize",
            f"{logo_scale * 100}%",
            logo_scaled_png_abs_path,
        ],
        # 3. Rasterize the shell snippet to the remaining width:
        [
            magick_executable,
            "-background",
            "none",
            "-density",
            str(shell_snippet_density_dpi),
            shell_snippet_svg_abs_path,
            "-resize",
            f"{shell_width_px}x",
            shell_snippet_png_abs_path,
        ],
        # 4. Compose both on the black canvas (logo flush left, shell snippet flush right):
        [
            magick_executable,
            "-size",
            f"{canvas_width_px}x{canvas_height_px}",
            "xc:black",
            logo_scaled_png_abs_path,
            "-geometry",
            f"+0+{top_offset_px}",
            "-composite",
            shell_snippet_png_abs_path,
            "-geometry",
            f"+{logo_size_px}+{top_offset_px}",
            "-composite",
            # Drop metadata (creation / modification timestamps) to get the same bytes on each run:
            "-strip",
            "-depth",
            "8",
            f"PNG24:{preview_png_abs_path}",
        ],
    ]


def parse_svg_width(svg_text: str) -> float:
    width_match = _svg_width_re.search(svg_text)
    if width_match is None:
        raise ValueError("`width` attribute not found in the root `<svg>` element")
    return float(width_match.group(1))
