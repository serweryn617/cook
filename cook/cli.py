import argparse
import pathlib

import questionary

from .main import Main


class Settings:
    def __init__(self):
        self.args = {}
        self.flags = []


settings = Settings()


def parse_user_args(user_args):
    args = {}
    flags = []

    for user_arg in user_args:
        if '=' in user_arg:
            key, value = user_arg.split('=')
            args[key] = value
        else:
            flags.append(user_arg)
    return args, flags


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

    parser.add_argument('-r', '--recipe_path', default='.', help='Path to directory containing `recipe.py` file.')
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('-f', '--format', action='store_true', help='Format output using Rich.')
    parser.add_argument('-t', '--targets', action='store_true', help='List available projects.')
    parser.add_argument('-d', '--dry', action='store_true', help='Dry run.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress stdout.')
    parser.add_argument(
        '-u', '--user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format either `key=value` or `flag`.'
    )
    parser.add_argument('-p', '--project', default=None, help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive project selection.')

    args = parser.parse_args()

    recipe_base_path = (pathlib.Path.cwd() / args.recipe_path).resolve()
    build_server = args.build_server
    project = args.project

    user_args, user_flags = parse_user_args(args.user_args)
    settings.args.update(user_args)
    settings.flags.extend(user_flags)

    rich_output = args.format
    quiet = args.quiet

    list_targets = args.targets
    dry_run = args.dry

    main_program = Main(recipe_base_path)
    main_program.initialize()

    if list_targets:
        projects, default_project = main_program.get_projects()
        recipe_path = main_program.get_recipe_path()
        print(f'Projects defined in {recipe_path}:')
        for project in projects:
            print('  ' + project, '<- default' if project == default_project else '')
        return

    if args.interactive:
        projects, default_project = main_program.get_projects()
        project = questionary.select('Project', choices=projects, default=default_project).ask()
        if project is None:
            exit(1)

    main_program.configure(project, build_server)
    main_program.set_output(rich_output, quiet)

    main_program.run(dry_run=dry_run)
