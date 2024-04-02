import importlib.util
import sys
from pathlib import Path
from cook import logger


class Recipe:
    def __init__(self, base_path: Path, user_args: dict):
        self.base_path = base_path
        self.user_args = user_args

        self.projects = None

        self.default_project = None
        self.default_build_server = 'local'

    def load(self):
        recipes = list(self.base_path.glob('recipe.py'))

        if len(recipes) == 0:
            logger.error(f'Recipe file not found in {self.base_path}')
            exit(1)

        recipe_file_path = str(recipes[0])
        module_name = 'recipe'

        spec = importlib.util.spec_from_file_location(module_name, recipe_file_path)
        recipe = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = recipe
        recipe.user_args = self.user_args  # Inject user_args to receipe.py before executing the module
        spec.loader.exec_module(recipe)

        if hasattr(recipe, 'projects'):
            self.projects = recipe.projects
        else:
            logger.error('No projects found in recipe.')
            exit(1)

        if hasattr(recipe, 'default_project'):
            self.default_project = recipe.default_project

        if hasattr(recipe, 'default_build_server'):
            self.default_build_server = recipe.default_build_server
