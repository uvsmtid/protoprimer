from inspect import (
    currentframe,
    getframeinfo,
)


def line_no() -> int:
    """
    Get source line in the caller frame
    """
    return _line_no_l_0()


def _line_no_l_0() -> int:
    """
    Line no from frame level 0 = callee frame = curr frame (from call site POV)
    """
    return getframeinfo(currentframe().f_back.f_back).lineno
