import sys

sys.dont_write_bytecode = True

import argparse
from pathlib import Path

from .library.logger import log
from .library.selector import SelectionInterrupt, Selector
from .main import Main
from .settings import settings
from .template import TEMPLATES
from collections.abc import Sequence
from collections.abc import Callable

type StepResult = int | None
type Step = Callable[[], StepResult]

class Cli:
    def __init__(self, project: str | None, build_server: str | None, interactive: bool, dry_run: bool, list_only: bool, template: int) -> None:
        self.project = project
        self.build_server = build_server

        self.interactive = interactive
        self.dry_run = dry_run
        self.list_only = list_only
        self.template = template

        self.recipe_base_path = Path.cwd().resolve()

    def generate_template(self) -> int | None:
        if self.template is None:
            return

        if not self.recipe_base_path.is_dir():
            log(f'{self.recipe_base_path} directory does not exist!', 'info')
            return 1

        recipe_path = self.recipe_base_path / f'recipe_template{self.template}.py'

        if recipe_path.is_file():
            log(f'recipe_template{self.template}.py already present in {self.recipe_base_path}', 'info')
            return 1

        with open(recipe_path, 'w') as file:
            file.write(TEMPLATES[self.template - 1])

        log(f'recipe_template{self.template}.py generated in {self.recipe_base_path}', 'log')
        return 0

    def search_for_recipe(self) -> int | None:
        dirs_to_check = [self.recipe_base_path] + list(self.recipe_base_path.parents)
        for directory in dirs_to_check:
            recipe_path = directory / 'recipe.py'
            if recipe_path.is_file():
                self.recipe_base_path = directory
                return
        log(f'recipe file not found in {self.recipe_base_path} or parent directories!', 'info')
        return 1

    def initialize_main(self) -> None:
        self.main_program = Main(self.recipe_base_path)
        self.main_program.initialize()

        self.projects, self.default_project = self.main_program.get_projects()
        self.build_servers, self.default_build_server = self.main_program.get_build_servers()

        self.project = self.project or self.default_project
        self.build_server = self.build_server or self.default_build_server

    def list_items(self) -> int | None:
        '''List build servers and projects defined in recipe file.'''
        if not self.list_only:
            return

        recipe_path = self.recipe_base_path / 'recipe.py'
        log(f'Items defined in {recipe_path}', bold=True, internal=False)

        self.list_item('Build Servers', self.build_servers, self.default_build_server)
        self.list_item('Projects', self.projects, self.default_project)

        return 0

        # TODO: parse user args interactively before loading the recipe

    @staticmethod
    def list_item(message: str, iterable: Sequence[str], default: str) -> None:
        if not iterable:
            log(f'{message} not defined.', 'warning')
            return

        log(f'{message}:', bold=True, internal=False)
        for item in iterable:
            if item == default:
                log(f' - {item} (default)', internal=False)
            else:
                log(f' - {item}', internal=False)

    def update_build_server(self) -> None:
        if self.build_server is None and len(self.build_servers) == 1:
            self.build_server = self.build_servers[0]

    def select_parameters_interactively(self) -> int | None:
        try:
            if self.interactive or self.project is None:
                self.project = select_interactively('Project', self.projects, self.default_project)

            if (self.interactive and len(self.build_servers) > 1) or self.build_server is None:
                self.build_server = select_interactively('Build Server', self.build_servers, self.default_build_server)

        except SelectionInterrupt:
            print("\nCancelled by user\n")
            return 1

    def configure_and_execute(self) -> None:
        self.main_program.configure(self.project, self.build_server)
        self.main_program.run(dry_run=self.dry_run)

    def run(self) -> int:
        steps: tuple[Step, ...] = (
            self.generate_template
            self.search_for_recipe
            self.initialize_main
            self.list_items
            self.update_build_server
            self.select_parameters_interactively
            self.configure_and_execute
        )

        for function in steps:
            return_code = function()
            if return_code is not None:
                return return_code
        return 0


def select_interactively(message, elements, default):
    if elements is None:
        return

    visible = tuple(filter(lambda s: not s.startswith("_"), elements))
    selected = Selector(visible, message, default=default).select()
    log(f'Selected {message}: {selected}', 'log')
    return selected


def cli():
    epilog_text = '\n'.join(
        (
            'example usage:',
            '  %(prog)s ./example my_project -b local -u name=latest --dry',
        )
    )

    parser = argparse.ArgumentParser(
        description='Build script aggregator and remote executor', epilog=epilog_text, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('project', default=None, nargs='?', help='Project to build. Uses value of `default_project` if left unspecified.')
    parser.add_argument('-b', '--build_server', help='Build server to use. Uses value of `default_build_server` if left unspecified.')
    parser.add_argument('-i', '--interactive', action='store_true', help='Use interactive project and build server selection.')
    parser.add_argument('-d', '--dry', action='store_true', help='Dry run.')
    parser.add_argument(
        '-u', '--user_args', nargs='*', default=[], help='User arguments. Can be used in recipe file. Format either `key=value` or `flag`.'
    )
    parser.add_argument('-l', '--list', action='store_true', help='List available projects and build servers.')
    parser.add_argument(
        '-t',
        '--template',
        nargs='?',
        type=int,
        default=None,
        const=1,
        choices=(1, 2, 3, 4),
        help='Generate recipe template in a selected directory.',
    )

    args = parser.parse_args()
    settings.update_user_args(args.user_args)
    app = Cli(args)
    return app.run()
