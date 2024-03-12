from rich import print as rprint

GREEN = '[#00cc52]'
PURPLE = '[#d849ff]'
RED = '[#ff0000]'

def local(message):
    rprint(GREEN + message)

def remote(message):
    rprint(PURPLE + message)

def error(message):
    rprint(RED + message)

