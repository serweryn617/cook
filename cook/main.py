import sys

from .configuration import ConfigurationError, ProjectConfiguration
from .exception import ProcessError
from .library.logger import log
from .recipe import Recipe, RecipeError
from .runner import ProjectRunner


class Main:
    def __init__(self, recipe_base_path: str) -> None:
        self.recipe_base_path = recipe_base_path
        self.project = None
        self.build_server = None

    def initialize(self) -> None:
        try:
            self.recipe = Recipe(self.recipe_base_path)
            self.recipe.load()
            self.configuration = ProjectConfiguration(self.recipe)

        except (RecipeError, ConfigurationError) as e:
            log(str(e), "error")
            sys.exit(1)

    def configure(self, project: str, build_server: str) -> None:
        self.project = project
        self.build_server = build_server

    def run(self, dry_run: bool = False) -> None:
        if dry_run:
            log("Dry run", "warning")

        try:
            self.configuration.setup(self.project, self.build_server)

            runner = ProjectRunner(self.recipe, self.configuration, dry_run)
            runner.run_project()

        except ConfigurationError as e:
            log(str(e), "error")
            sys.exit(1)

        except ProcessError as e:
            log(str(e), "error")
            sys.exit(e.return_code)

        log(f"Finished running {self.project} on {self.build_server}", "info")

        if dry_run:
            log("Dry run finished", "warning")

    def get_projects(self) -> tuple[list[str], str | None]:
        projects = self.configuration.get_project_names()
        default_project = self.recipe.default_project
        return projects, default_project

    def get_build_servers(self):
        return self.configuration.build_servers, self.recipe.default_build_server
