from rich.console import Console
from rich.theme import Theme

GREEN = '#00cc52'
PURPLE = '#d849ff'
RED = '#ff0000'


class Logger:
    def __init__(self):
        cook_console_theme = Theme(
            {
                'local': GREEN,
                'remote': PURPLE,
                'error': RED,
            }
        )
        self.console = Console(theme=cook_console_theme)

    def _internal_message(self, message, style):
        message = '=== ' + str(message) + ' ==='
        self.console.print(message, style=style, highlight=False)

    def local(self, message):
        self._internal_message(message, 'local')

    def remote(self, message):
        self._internal_message(message, 'remote')

    def error(self, message):
        self._internal_message(message, 'error')

    def rich(self, message):
        self.console.print(message, end='')

    def raw(self, message):
        print(message, end='')
