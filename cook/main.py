from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .exception import ProcessError
from .library.logger import log
from .recipe import Recipe, RecipeError


class Main:
    def __init__(self, recipe_base_path):
        self.recipe_base_path = recipe_base_path
        self.project = None
        self.build_server = None

    def get_recipe_path(self):
        return (self.recipe.base_path / "recipe.py").as_posix()

    def get_projects(self):
        projects = list(self.recipe.projects.keys())
        default_project = self.recipe.default_project
        return projects, default_project

    def get_build_servers(self):
        return self.configuration.build_servers, self.recipe.default_build_server

    def configure(self, project, build_server):
        self.project = project
        self.build_server = build_server

    def initialize(self):
        try:
            self.recipe = Recipe(self.recipe_base_path)
            self.recipe.load()
            self.configuration = Configuration(self.recipe)

        except (RecipeError, ConfigurationError) as e:
            log(e, 'error')
            exit(1)  # TODO: use sys.exit?

    def run(self, dry_run=False):
        if dry_run:
            log('Dry run', 'warning')

        try:
            self.configuration.setup(self.project, self.build_server)

            self.cook = Cook(self.recipe, self.configuration, dry_run)
            self.cook.cook()

        except ConfigurationError as e:
            log(e, 'error')
            exit(1)

        except ProcessError as e:
            log(e, 'error')
            exit(e.return_code)

        log(f'Finished running {self.project} on {self.build_server}', 'info')

        if dry_run:
            log('Dry run finished', 'warning')
