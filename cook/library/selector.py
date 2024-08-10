import sys

from .key import getkey


class SelectionInterrupt(Exception):
    pass


class ansi:
    up = lambda n: f'\x1B[{n}A'
    down = lambda n: f'\x1B[{n}B'
    right = lambda n: f'\x1B[{n}C'
    left = lambda n: f'\x1B[{n}D'

    line_begin = '\x1B[1G'

    hide_cursor = '\x1B[?25l'
    show_cursor = '\x1B[?25h'

    clear_after_cursor = '\x1B[0J'


class Selector:
    def __init__(self, elements: tuple | list, message: str = '', cursor: str = '>'):
        self.elements = elements
        self.num = len(elements)
        self.cursor = cursor
        self.cursor_len = len(cursor)
        self.message = message
        assert self.cursor_len > 0, 'Cursor must be at least 1 character!'

    def select(self):
        print(f'Select{' ' + self.message if self.message else ''}')
        print(ansi.hide_cursor, end='')

        for elem in self.elements:
            print(' ', ' ' * self.cursor_len, ' ', elem, sep='')
        print(ansi.up(self.num) + ansi.right(1), end='')

        current = 0
        prev_current = 0

        if current:
            print(ansi.down(current), end='')
        print(self.cursor + ansi.left(self.cursor_len), end='')
        sys.stdout.flush()

        while True:
            c = getkey()
            if c == '\x1B[A':
                current -= 1
            elif c == '\x1B[B':
                current += 1
            elif c == '\r':
                break
            else:
                self._cleanup(current)
                raise SelectionInterrupt
            current %= self.num

            if current != prev_current:
                move = ansi.down(current - prev_current) if current > prev_current else ansi.up(prev_current - current)
                prev_current = current

                print(' ' * self.cursor_len + ansi.left(self.cursor_len), end='')
                print(move, end='')
                print(self.cursor + ansi.left(self.cursor_len), end='')
                sys.stdout.flush()

        self._cleanup(current)
        print(f'Selected{' ' + self.message if self.message else ''}:', self.elements[current])
        return self.elements[current]

    def _cleanup(self, current):
        print(ansi.up(current + 1) + ansi.line_begin, end='')
        print(ansi.clear_after_cursor, end='')
        print(ansi.show_cursor, end='')
        sys.stdout.flush()
