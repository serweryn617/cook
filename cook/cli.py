import argparse
import pathlib

from .cook import Cook
from .receipe import Receipe
from .configuration import Configuration


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('project', nargs='?')
    parser.add_argument('build_server', nargs='?')

    args = parser.parse_args()

    base_path = pathlib.Path.cwd()

    receipe = Receipe(base_path)
    receipe.load()

    configuration = Configuration(receipe)
    configuration.setup(args.project, args.build_server)

    cook = Cook(receipe, configuration)
    cook.cook()


if __name__ == '__main__':
    main()