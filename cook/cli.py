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
    parser.add_argument('-p', '--recipe_path', default='.', help='Recipe file directory path.')
    parser.add_argument('options', nargs='*', default={}, help='Project to build followed by user arguments.') #  Uses value of `default_project` if left unspecified, Can be used in recipe file. Format: key=value
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')

    args = parser.parse_args()
    recipe_base_path = pathlib.Path.cwd() / args.recipe_path
    build_server = args.build_server
    if args.options and '=' in args.options[0]:
        project = None
    else:
        project = args.options.pop(0)
    user_args = parse_user_args(args.options)

    recipe = Recipe(recipe_base_path, user_args)
    recipe.load()

    configuration = Configuration(recipe)
    configuration.setup(project, build_server)

    cook = Cook(recipe, configuration)
    cook.cook()


if __name__ == '__main__':
    main()