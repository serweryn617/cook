import argparse
import pathlib

from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .executors import ProcessError
from .logger import Logger
from .recipe import NoProjectsDefined, Recipe, RecipeNotFound


def parse_user_args(user_args):
    res = {}
    for arg in user_args:
        key, value = arg.split('=')
        res[key] = value
    return res


def main():
    epilog_text = '\n'.join(
        (
            'example usage:',
            '  %(prog)s my_project name=latest -p ./example/ -b local',
        )
    )

    parser = argparse.ArgumentParser(
        description='Build script aggregator and remote executor', epilog=epilog_text, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-p', '--recipe_path', default='.', help='Path to directory containing `recipe.py` file.')
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('project', nargs='?', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format: `key=value`')

    args = parser.parse_args()
    recipe_base_path = pathlib.Path.cwd() / args.recipe_path
    build_server = args.build_server
    if args.project and '=' in args.project:
        project = None
        args.user_args.append(args.project)
    else:
        project = args.project
    user_args = parse_user_args(args.user_args)

    # Recipe
    recipe = Recipe(recipe_base_path, user_args)
    try:
        recipe.load()
    except (RecipeNotFound, NoProjectsDefined) as e:
        Logger().error(e)
        exit(1)

    # Project configuration
    configuration = Configuration(recipe)
    try:
        configuration.setup(project, build_server)
    except ConfigurationError as e:
        Logger().error(e)
        exit(1)

    # Cook!
    cook = Cook(recipe, configuration)
    try:
        cook.cook()
    except ProcessError as e:
        Logger().error(e)
        exit(e.return_code)


if __name__ == '__main__':
    main()
