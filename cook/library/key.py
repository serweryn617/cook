import sys

from .terminal import EscapeCodes


def getchars_unix(num=1):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(num)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def getchar_windows():
    # if msvcrt.kbhit():
    return msvcrt.getchar()


if sys.platform.startswith('linux'):
    import termios
    import tty

    getchar = getchars_unix
else:
    import msvcrt

    getchar = getchar_windows


def getkey() -> str:
    c = getchar()
    if c == EscapeCodes.escape:
        c += getchar(2)
    return c
