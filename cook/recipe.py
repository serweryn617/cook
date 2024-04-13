import importlib
import sys
from pathlib import Path
from typing import Any


class RecipeNotFound(Exception):
    pass


class RecipeError(Exception):
    pass


class Recipe:
    default_project: str
    default_build_server: str
    projects: dict[dict[Any]]

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def load(self):
        recipes = list(self.base_path.glob('recipe.py'))

        if len(recipes) == 0:
            raise RecipeNotFound(f'Recipe file not found in {self.base_path}')

        recipe_file_path = Path(recipes[0])
        module_name = 'recipe'

        sys.path.insert(0, recipe_file_path.parent.as_posix())
        recipe = importlib.import_module(module_name)

        self.update(vars(recipe))

    def update(self, settings):
        for key in self.__annotations__.keys():
            try:
                value = settings[key]
            except KeyError:
                raise RecipeError(f'{key} entry not found in recipe.')
            setattr(self, key, value)
