import argparse
import pathlib

from .main import main


class Settings:
    def __init__(self):
        self.args = {}
        self.flags = []


settings = Settings()


def parse_user_args(user_args):
    res = {}
    for arg in user_args:
        key, value = arg.split('=')
        res[key] = value
    return res


def cli():
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
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress stdout.')
    parser.add_argument('project', nargs='?', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format: `key=value`')

    # TODO: add user flag args
    # TODO: use better user args, e.g. --name latest

    args = parser.parse_args()
    recipe_base_path = (pathlib.Path.cwd() / args.recipe_path).resolve()
    build_server = args.build_server
    if args.project and '=' in args.project:
        project = None
        args.user_args.insert(0, args.project)
    else:
        project = args.project
    settings.args.update(parse_user_args(args.user_args))
    rich_output = args.rich_output
    quiet = args.quiet

    list_targets = args.targets
    dry_run = args.dry

    main(recipe_base_path, project, build_server, rich_output, quiet, dry_run, list_targets)
