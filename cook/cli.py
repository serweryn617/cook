import argparse
import pathlib

from .cook import Cook
from .recipe import Recipe
from .configuration import Configuration


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('recipe_path', nargs='?', default='.', help='Recipe file directory path.')
    parser.add_argument('-p', '--project', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-s', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')

    args = parser.parse_args()

    base_path = pathlib.Path.cwd() / args.recipe_path

    recipe = Recipe(base_path)
    recipe.load()

    configuration = Configuration(recipe)
    configuration.setup(args.project, args.build_server)

    cook = Cook(recipe, configuration)
    cook.cook()


if __name__ == '__main__':
    main()