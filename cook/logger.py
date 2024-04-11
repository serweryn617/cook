from rich import print as rprint
from rich.console import Console

GREEN = '[#00cc52]'
PURPLE = '[#d849ff]'
RED = '[#ff0000]'

console = Console()

def process(message):
    message = message.replace('[', '\[')
    return '=== ' + message + ' ==='

def local(message):
    console.print(GREEN + process(message))

def remote(message):
    console.print(PURPLE + process(message))

def error(message):
    console.print(RED + process(message))

def auto(message):
    console.print(message, end='')

