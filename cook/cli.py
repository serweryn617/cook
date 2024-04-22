import argparse
import pathlib

from .main import main, settings


def parse_user_args(user_args):
    res = {}
    for arg in user_args:
        key, value = arg.split('=')
        res[key] = value
    return res


def cli():
    global settings

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
    parser.add_argument('-r', '--rich_output', action='store_true', help='Use Rich to format output.')
    parser.add_argument('-t', '--targets', action='store_true', help='List available projects.')
    parser.add_argument('-d', '--dry', action='store_true', help='Dry run.')
    parser.add_argument('project', nargs='?', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format: `key=value`')

    # TODO: add quiet option
    # TODO: add user flag args
    # TODO: use better user args, e.g. --name latest

    args = parser.parse_args()
    settings.recipe_base_path = (pathlib.Path.cwd() / args.recipe_path).resolve()
    settings.build_server = args.build_server
    if args.project and '=' in args.project:
        settings.project = None
        args.user_args.insert(0, args.project)
    else:
        settings.project = args.project
    settings.user_args.update(parse_user_args(args.user_args))
    settings.rich_output = args.rich_output

    if args.targets:
        settings.mode = 'targets'
    elif args.dry:
        settings.mode = 'dry'

    main()
