import argparse
import pathlib

from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .executors import ExecutorProcessError
from .logger import Logger
from .recipe import NoProjectsDefined, Recipe, RecipeNotFound

user_args = {}


def parse_user_args(user_args):
    res = {}
    for arg in user_args:
        key, value = arg.split('=')
        res[key] = value
    return res


def main():
    global user_args

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
    parser.add_argument('-r', '--rich_output', action='store_true')
    parser.add_argument('project', nargs='?', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format: `key=value`')

    args = parser.parse_args()
    recipe_base_path = pathlib.Path.cwd() / args.recipe_path
    build_server = args.build_server
    if args.project and '=' in args.project:
        project = None
        args.user_args.insert(0, args.project)
    else:
        project = args.project
    user_args.update(parse_user_args(args.user_args))
    rich_output = args.rich_output

    try:
        recipe = Recipe(recipe_base_path, user_args)
        recipe.load()

        configuration = Configuration(recipe)
        configuration.setup(project, build_server)

        cook = Cook(recipe, configuration, rich_output)
        cook.cook()

    except (RecipeNotFound, NoProjectsDefined, ConfigurationError) as e:
        Logger().error(e)
        exit(1)

    except ExecutorProcessError as e:
        Logger().error(e)
        exit(e.return_code)


if __name__ == '__main__':
    main()
