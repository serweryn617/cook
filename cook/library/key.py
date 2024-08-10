import sys


class Getchar:
    def __init__(self):
        if sys.platform.startswith('linux'):
            self.implementation = GetcharUnix()
        else:
            self.implementation = GetcharWindows()

    def getchar(self, num=1):
        return self.implementation.getchar(num)


class GetcharUnix:
    def __init__(self):
        import termios
        import tty

        self.tty = tty
        self.termios = termios

    def getchar(self, num=1):
        fd = sys.stdin.fileno()
        old_settings = self.termios.tcgetattr(fd)
        try:
            self.tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(num)
        finally:
            self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)
        return char


class GetcharWindows:
    def __init__(self):
        import msvcrt

        self.msvcrt = msvcrt

    def getchar(self):
        # if msvcrt.kbhit():
        return self.msvcrt.getchar()


getchar = Getchar()


def getkey() -> str:
    c = getchar.getchar()
    if c == '\x1B':
        c += getchar.getchar(2)
    return c
