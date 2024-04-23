from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .exception import ProcessError
from .executors import ExecutorError
from .logger import Logger
from .recipe import Recipe, RecipeError, RecipeNotFound


class Main:
    def __init__(self, recipe_base_path, project, build_server, rich_output=False, quiet=False):
        self.recipe_base_path = recipe_base_path
        self.project = project
        self.build_server = build_server
        self.rich_output = rich_output
        self.quiet = quiet

    def get_recipe_path(self):
        return (self.recipe.base_path / "recipe.py").as_posix()

    def get_projects(self):
        projects = list(self.recipe.projects.keys())
        default_project = self.recipe.default_project
        return projects, default_project

    def initialize(self):
        self.logger = Logger(self.rich_output, self.quiet)

        if self.rich_output and self.quiet:
            self.logger.print('warning', 'Suppressing stdout and using formatted output will also suppress stderr!')

        try:
            self.recipe = Recipe(self.recipe_base_path)
            self.recipe.load()

            self.configuration = Configuration(self.recipe)
            self.configuration.setup(self.project, self.build_server)

            self.cook = Cook(self.recipe, self.configuration, self.logger)

        except (RecipeNotFound, RecipeError, ConfigurationError) as e:
            logger.print('error', e)
            exit(1)

    def run(self, dry_run=False):
        try:
            self.cook.set_dry_run(dry_run)
            self.cook.cook()

        except ProcessError as e:
            logger.print('error', e)
            exit(e.return_code)

        except ExecutorError as e:
            logger.print('error', f'{e.name}: {e}')
            exit(e.return_code)
