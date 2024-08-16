import sys

from .terminal import EscapeCodes, UnixKeys, WindowsKeys


def _getchars_unix(num=1):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    try:
        char = sys.stdin.read(num)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def _getkey_unix() -> str:
    c = _getchars_unix()
    if c == UnixKeys.escape:
        c += _getchars_unix(2)
    return c


def _getchar_windows():
    return msvcrt.getwch()


def _getkey_windows() -> str:
    c = _getchar_windows()
    if c == WindowsKeys.escape:
        c += _getchar_windows()
    return c


if sys.platform.startswith('linux'):
    import termios
    import tty

    getkey = _getkey_unix
else:
    import msvcrt

    getkey = _getkey_windows
