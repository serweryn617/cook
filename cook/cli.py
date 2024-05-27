import argparse
import pathlib

import questionary
from rich import print as rprint

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
            '  %(prog)s -p my_project -u name=latest -r ./example/ -b local',
        )
    )

    parser = argparse.ArgumentParser(
        description='Build script aggregator and remote executor', epilog=epilog_text, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('recipe_path', default='.', nargs='?', help='Path to directory containing `recipe.py` file. Defaults to CWD.')
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('-f', '--format', action='store_true', help='Format output using Rich.')
    parser.add_argument('-l', '--list', action='store_true', help='List available projects and build servers.')
    parser.add_argument('-d', '--dry', action='store_true', help='Dry run.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress stdout.')
    parser.add_argument(
        '-u', '--user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format either `key=value` or `flag`.'
    )
    parser.add_argument('-p', '--project', default=None, help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-i', '--interactive', action='store_true', help='Force interactive selection.')

    args = parser.parse_args()

    user_args, user_flags = parse_user_args(args.user_args)
    settings.args.update(user_args)
    settings.flags.extend(user_flags)

    rich_output = args.format
    quiet = args.quiet

    to_list = args.list
    dry_run = args.dry

    recipe_base_path = (pathlib.Path.cwd() / args.recipe_path).resolve()
    main_program = Main(recipe_base_path)
    main_program.initialize()

    projects, default_project = main_program.get_projects()
    build_servers, default_build_server = main_program.get_build_servers()

    project = args.project or default_project
    build_server = args.build_server or default_build_server

    if to_list:
        recipe_path = main_program.get_recipe_path()
        rprint(f'[bold]Items defined in {recipe_path}')

        rprint('[bold #fcac00]Build Servers[/]:')
        for build_server in build_servers:
            if build_server == default_build_server:
                msg = f'  [#555555 on #cccccc]{build_server}[/]'
            else:
                msg = f'  {build_server}'
            rprint(msg)

        rprint('[bold #fcac00]Projects[/]:')
        for project in projects:
            if project == default_project:
                msg = f'  [#555555 on #cccccc]{project}[/]'
            else:
                msg = f'  {project}'
            rprint(msg)
        return

    # TODO: parse user args interactively before loading the recipe
    if args.interactive or project is None:
        project = questionary.select('Project', choices=projects, default=default_project).ask()
        if project is None:
            exit(1)

    if args.interactive or build_server is None:
        build_server = questionary.select('Build Server', choices=build_servers, default=default_build_server).ask()
        if build_server is None:
            exit(1)

    main_program.configure(project, build_server)
    main_program.set_output(rich_output, quiet)

    main_program.run(dry_run=dry_run)
