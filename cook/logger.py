from rich import print as rprint

GREEN = '[#00cc52]'
PURPLE = '[#d849ff]'
RED = '[#ff0000]'

def process(message):
    message = message.replace('[', '\[')
    return '=== ' + message + ' ==='

def local(message):
    rprint(GREEN + process(message))

def remote(message):
    rprint(PURPLE + process(message))

def error(message):
    rprint(RED + process(message))

