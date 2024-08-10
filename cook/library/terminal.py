class ansi:
    fg = lambda r, g, b: f'\x1B[38;2;{r};{g};{b}m'
    bg = lambda r, g, b: f'\x1B[48;2;{r};{g};{b}m'

