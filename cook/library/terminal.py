class EscapeCodes:
    escape = '\x1B'

    up = lambda n: f'\x1B[{n}A'
    down = lambda n: f'\x1B[{n}B'
    right = lambda n: f'\x1B[{n}C'
    left = lambda n: f'\x1B[{n}D'

    line_begin = '\x1B[1G'

    hide_cursor = '\x1B[?25l'
    show_cursor = '\x1B[?25h'
    clear_after_cursor = '\x1B[0J'

    fg = lambda r, g, b: f'\x1B[38;2;{r};{g};{b}m'
    bg = lambda r, g, b: f'\x1B[48;2;{r};{g};{b}m'

    bold = '\x1B[1m'
    bold_reset = '\x1B[22m'
    reset = '\x1B[0m'
