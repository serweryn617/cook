from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .exception import ProcessError
from .executors import ExecutorError
from .logger import Logger
from .recipe import Recipe, RecipeError, RecipeNotFound


class Main:
    def __init__(self, recipe_base_path):
        self.recipe_base_path = recipe_base_path
        self.project = None
        self.build_server = None
        self.rich_output = False
        self.quiet = False

    def get_recipe_path(self):
        return (self.recipe.base_path / "recipe.py").as_posix()

    def get_projects(self):
        projects = list(self.recipe.projects.keys())
        default_project = self.recipe.default_project
        return projects, default_project

    def get_build_servers(self):
        return self.recipe.build_servers, self.recipe.default_build_server

    def configure(self, project, build_server):
        self.project = project
        self.build_server = build_server

    def set_output(self, rich=False, quiet=False):
        self.rich_output = rich
        self.quiet = quiet

        if self.rich_output and self.quiet:
            self.logger.print('warning', 'Suppressing stdout and using formatted output will also suppress stderr!')

    def initialize(self):
        self.logger = Logger(self.rich_output, self.quiet)

        try:
            self.recipe = Recipe(self.recipe_base_path)
            self.recipe.load()

        except (RecipeNotFound, RecipeError) as e:
            self.logger.print('error', e)
            exit(1)

    def run(self, dry_run=False):
        if dry_run:
            self.logger.print('warning', 'Dry run')

        try:
            self.configuration = Configuration(self.recipe)
            self.configuration.setup(self.project, self.build_server)

            self.cook = Cook(self.recipe, self.configuration, self.logger)
            self.cook.set_dry_run(dry_run)
            self.cook.cook()

        except ConfigurationError as e:
            self.logger.print('error', e)
            exit(1)

        except ProcessError as e:
            self.logger.print('error', e)
            exit(e.return_code)

        except ExecutorError as e:
            self.logger.print('error', f'{e.name}: {e}')
            exit(e.return_code)

        self.logger.print('info', f'Finished running {self.project} on {self.build_server}')

        if dry_run:
            self.logger.print('warning', 'Dry run finished')
