import os

# TODO: TODO_50_98_96_87.support_windows.md: "Test suite hardcodes POSIX path separators ..." (Option B):
# a POSIX-style literal is not absolute on Windows (`C:` drive, `\` separator, and `ntpath.isabs("/abs")` is `False` since `python` 3.13).


def abs_path(posix_abs_path: str) -> str:
    """
    Convert a POSIX-style absolute path literal (e.g. `/ref_root/dst`) into an absolute path of the running platform.

    It is the identity on POSIX (for a normalized path).
    """
    return os.path.abspath(posix_abs_path)
