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
    epilog_text = '\n'.join((
        'example usage:',
        '  %(prog)s my_project name=latest -p ./example/ -b local',
    ))

    parser = argparse.ArgumentParser(
        description='Build script aggregator and remote executor',
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
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

    recipe = Recipe(recipe_base_path, user_args)
    recipe.load()

    configuration = Configuration(recipe)
    configuration.setup(project, build_server)

    cook = Cook(recipe, configuration)
    cook.cook()


if __name__ == '__main__':
    main()