import argparse
import os
import pathlib
import sys

from .cook import Cook


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('project', nargs='?')
    parser.add_argument('build_server', nargs='?')

    args = parser.parse_args()

    base_path = pathlib.Path.cwd()

    cook = Cook(base_path, args.project, args.build_server)
    cook.cook()


if __name__ == '__main__':
    main()