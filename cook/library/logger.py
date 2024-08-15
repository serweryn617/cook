from .terminal import EscapeCodes

GREEN = 0x00, 0xCC, 0x52
PURPLE = 0xD8, 0x49, 0xFF
ORANGE = 0xFF, 0x88, 0x00
RED = 0xFF, 0x00, 0x00

THEME = {
    'log': GREEN,
    'info': PURPLE,
    'warning': ORANGE,
    'error': RED,
}


def log(message, style=None, bold=False, internal=True):
    message = str(message)

    if internal:
        message = '==> ' + message

    if bold:
        message = EscapeCodes.bold + message + EscapeCodes.reset

    if style:
        color = EscapeCodes.fg(*THEME[style])
        message = color + message + EscapeCodes.reset

    print(message)
