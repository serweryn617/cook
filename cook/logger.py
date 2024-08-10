from .library.terminal import ansi


class Logger:
    GREEN = 0x00, 0xCC, 0x52
    PURPLE = 0xD8, 0x49, 0xFF
    ORANGE = 0xFF, 0x88, 0x00
    RED = 0xFF, 0x00, 0x00

    theme = {
        'log': GREEN,
        'info': PURPLE,
        'warning': ORANGE,
        'error': RED,
    }

    def __init__(self, rich_output=True):
        self.rich_output = True
        self.quiet = False
        self.silent = False

    def __call__(self, message, style=None, bold=False):
        if self.quiet:
            return

        if style is None:
            print(message)
            return

        message = '=== ' + str(message) + ' ==='
        color = ansi.fg(*self.theme[style])
        message = color + message

        if bold:
            message = ansi.bold + message

        print(message + ansi.reset)


log = Logger()
