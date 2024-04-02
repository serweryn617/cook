import argparse
import pathlib

from .cook import Cook
from .recipe import Recipe
from .configuration import Configuration


def parse_user_args(user_args):
    res = {}
    for arg in user_args:
        key, value = arg.split('=')
        res[key] = value
    return res


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('recipe_path', nargs='?', default='.', help='Recipe file directory path.')
    parser.add_argument('-p', '--project', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-s', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('-u', '--user_args', nargs='*', default={}, help='User arguments. Can be used in recipe file. Format: key=value')

    args = parser.parse_args()

    base_path = pathlib.Path.cwd() / args.recipe_path
    user_args = parse_user_args(args.user_args)

    recipe = Recipe(base_path, user_args)
    recipe.load()

    configuration = Configuration(recipe)
    configuration.setup(args.project, args.build_server)

    cook = Cook(recipe, configuration)
    cook.cook()


if __name__ == '__main__':
    main()