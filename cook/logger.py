from rich.console import Console
from rich.theme import Theme


class Logger:
    GREEN = '#00cc52'
    PURPLE = '#d849ff'

    def __init__(self, rich_output, quiet):
        cook_console_theme = Theme(
            {
                'log': Logger.GREEN,
                'info': Logger.PURPLE,
                'warning': 'dark_orange',
                'error': 'red',
            }
        )
        self.console = Console(theme=cook_console_theme)
        self.rich_output = rich_output
        self.quiet = quiet

    def print(self, style, message):
        message = '=== ' + str(message) + ' ==='
        self.console.print(message, style=style, highlight=False)

    def log(self, message):
        if self.quiet:
            return

        if self.rich_output:
            self.console.print(message, end='')
        else:
            print(message, end='')

    def use_rich_output(self):
        return self.rich_output

    def is_quiet(self):
        return self.quiet
