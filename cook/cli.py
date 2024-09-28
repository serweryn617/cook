import argparse
from pathlib import Path

from .library.logger import log
from .library.selector import SelectionInterrupt, Selector
from .main import Main
from .template.recipe_template import TEMPLATE


class Settings:
    def __init__(self):
        self.args = {}
        self.flags = []


settings = Settings()


def list_items(recipe_path, build_servers, default_build_server, projects, default_project):
    log(f'Items defined in {recipe_path}', bold=True, internal=False)

    list_item('Build Servers', build_servers, default_build_server)
    list_item('Projects', projects, default_project)


def list_item(message, iterable, default):
    if not iterable:
        log(f'{message} not defined.', 'warning')
        return

    log(f'{message}:', bold=True, internal=False)
    for item in iterable:
        if item == default:
            log(f' - {item} (default)', internal=False)
        else:
            log(f' - {item}', internal=False)


def select_interactively(message, elements, default):
    if elements is None:
        return

    visible = tuple(filter(lambda s: not s.startswith("_"), elements))
    selected = Selector(visible, message, default=default).select()
    log(f'Selected {message}: {selected}', 'log')
    return selected


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


def generate_template(base_path: Path):
    if not base_path.is_dir():
        log(f'{base_path} directory does not exist!', 'info')
        return 1

    recipe_path = base_path / 'recipe.py'

    if recipe_path.is_file():
        log(f'recipe.py already present in {base_path}', 'info')
        return 1

    with open(recipe_path, 'w') as file:
        file.write(TEMPLATE)

    log(f'recipe.py generated in {base_path}', 'log')
    return 0


def cli():
    epilog_text = '\n'.join(
        (
            'example usage:',
            '  %(prog)s ./example -p my_project -b local -u name=latest --dry',
        )
    )

    parser = argparse.ArgumentParser(
        description='Build script aggregator and remote executor', epilog=epilog_text, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('recipe_path', default='.', nargs='?', help='Path to directory containing `recipe.py` file. Defaults to CWD.')
    parser.add_argument('-p', '--project', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('-i', '--interactive', action='store_true', help='Use interactive project and build server selection.')
    parser.add_argument('-d', '--dry', action='store_true', help='Dry run.')
    parser.add_argument(
        '-u', '--user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format either `key=value` or `flag`.'
    )
    parser.add_argument('-l', '--list', action='store_true', help='List available projects and build servers and exit.')
    parser.add_argument('-t', '--generate_template', action='store_true', help='Genereta recipe template in a selected directory.')

    args = parser.parse_args()

    user_args, user_flags = parse_user_args(args.user_args)
    settings.args.update(user_args)
    settings.flags.extend(user_flags)

    to_list = args.list
    dry_run = args.dry

    recipe_base_path = (Path.cwd() / args.recipe_path).resolve()

    if args.generate_template:
        return generate_template(recipe_base_path)

    main_program = Main(recipe_base_path)
    main_program.initialize()

    projects, default_project = main_program.get_projects()
    build_servers, default_build_server = main_program.get_build_servers()

    project = args.project or default_project
    build_server = args.build_server or default_build_server

    if to_list:
        recipe_path = main_program.get_recipe_path()
        list_items(recipe_path, build_servers, default_build_server, projects, default_project)
        return 0

    # TODO: parse user args interactively before loading the recipe

    try:
        if args.interactive or project is None:
            project = select_interactively('Project', projects, default_project)

        if args.interactive or build_server is None:
            build_server = select_interactively('Build Server', build_servers, default_build_server)

    except SelectionInterrupt:
        print("\nCancelled by user\n")
        return 1

    main_program.configure(project, build_server)
    main_program.run(dry_run=dry_run)
