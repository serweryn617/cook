from .library.terminal import ansi


class Logger:
    GREEN = 0x00, 0xcc, 0x52
    PURPLE = 0xd8, 0x49, 0xff
    ORANGE = 0xff, 0x88, 0x00
    RED = 0xff, 0x00, 0x00

    theme = {
        'log': GREEN,
        'info': PURPLE,
        'warning': ORANGE,
        'error': RED,
    }

    def __init__(self, rich_output, quiet):
        self.rich_output = rich_output
        self.quiet = quiet

    def print(self, style, message):
        message = '=== ' + str(message) + ' ==='
        color = ansi.fg(*self.theme[style])
        print(color + message)

    def log(self, message):
        if self.quiet:
            return

        print(message, end='')

    def use_rich_output(self):
        return self.rich_output

    def is_quiet(self):
        return self.quiet
