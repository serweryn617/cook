import sys

from .key import getkey
from .logger import ORANGE
from .terminal import EscapeCodes, UnixKeys, WindowsKeys


class SelectionInterrupt(Exception):
    pass


class Selector:
    def __init__(self, elements: tuple | list, message: str = '', cursor: str = '>', default=None):
        self.elements = elements
        self.num = len(elements)
        self.cursor = cursor
        self.cursor_len = len(cursor)
        self.message = message
        assert self.cursor_len > 0, 'Cursor must be at least 1 character!'

        self.default_index = elements.index(default) if default is not None else 0

    def select(self):
        print(EscapeCodes.fg(*ORANGE) + f'Select{" " + self.message if self.message else ""}:' + EscapeCodes.reset)
        print(EscapeCodes.hide_cursor, end='')

        for elem in self.elements:
            print(' ', ' ' * self.cursor_len, ' ', elem, sep='')
        print(EscapeCodes.up(self.num) + EscapeCodes.right(1), end='')

        current = self.default_index
        prev_current = current

        if current:
            print(EscapeCodes.down(current), end='')
        print(self.cursor + EscapeCodes.left(self.cursor_len), end='')
        sys.stdout.flush()

        while True:
            c = getkey()
            if c in (UnixKeys.up, WindowsKeys.up, 'k'):
                current -= 1
            elif c in (UnixKeys.down, WindowsKeys.down, 'j'):
                current += 1
            elif c == '\r':
                break
            else:
                self._cleanup(current)
                raise SelectionInterrupt
            current %= self.num

            if current != prev_current:
                move = EscapeCodes.down(current - prev_current) if current > prev_current else EscapeCodes.up(prev_current - current)
                prev_current = current

                print(' ' * self.cursor_len + EscapeCodes.left(self.cursor_len), end='')
                print(move, end='')
                print(self.cursor + EscapeCodes.left(self.cursor_len), end='')
                sys.stdout.flush()

        self._cleanup(current)
        return self.elements[current]

    def _cleanup(self, current):
        print(EscapeCodes.up(current + 1) + EscapeCodes.line_begin, end='')
        print(EscapeCodes.clear_after_cursor, end='')
        print(EscapeCodes.show_cursor, end='')
        sys.stdout.flush()
