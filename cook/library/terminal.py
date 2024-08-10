class ansi:
    fg = lambda r, g, b: f'\x1B[38;2;{r};{g};{b}m'
    bg = lambda r, g, b: f'\x1B[48;2;{r};{g};{b}m'

    bold = '\x1B[1m'
    bold_reset = '\x1B[22m'
    reset = '\x1B[0m'
