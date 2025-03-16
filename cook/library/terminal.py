class EscapeCodes:
    up = lambda n: f'\x1b[{n}A'
    down = lambda n: f'\x1b[{n}B'
    right = lambda n: f'\x1b[{n}C'
    left = lambda n: f'\x1b[{n}D'

    line_begin = '\x1b[1G'

    hide_cursor = '\x1b[?25l'
    show_cursor = '\x1b[?25h'
    clear_after_cursor = '\x1b[0J'

    fg = lambda r, g, b: f'\x1b[38;2;{r};{g};{b}m'
    bg = lambda r, g, b: f'\x1b[48;2;{r};{g};{b}m'

    bold = '\x1b[1m'
    bold_reset = '\x1b[22m'
    reset = '\x1b[0m'


class UnixKeys:
    escape = '\x1b'
    up = '\x1b[A'
    down = '\x1b[B'


class WindowsKeys:
    escape = "\xe0"
    up = "\xe0H"
    down = "\xe0P"
