from .terminal import ansi


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

    def __init__(self):
        self.formatted = True
        self.silent = False

    def __call__(self, message, style=None, bold=False, internal=True):
        if self.silent:
            return

        message = str(message)

        if internal:
            message = '==> ' + message

        if bold:
            message = ansi.bold + message + ansi.reset

        if style:
            color = ansi.fg(*self.theme[style])
            message = color + message + ansi.reset

        print(message)


log = Logger()