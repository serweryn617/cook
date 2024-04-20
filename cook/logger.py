from rich.console import Console
from rich.theme import Theme


class Logger:
    GREEN = '#00cc52'
    PURPLE = '#d849ff'

    def __init__(self, log_rich_output):
        cook_console_theme = Theme(
            {
                'local': Logger.GREEN,
                'remote': Logger.PURPLE,
                'warning': 'dark_orange',
                'error': 'red',
            }
        )
        self.console = Console(theme=cook_console_theme)
        self.log_rich_output = log_rich_output

    def print(self, style, message):
        message = '=== ' + str(message) + ' ==='
        self.console.print(message, style=style, highlight=False)

    def log(self, message):
        if self.log_rich_output:
            self.console.print(message, end='')
        else:
            print(message, end='')
