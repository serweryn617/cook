import importlib
import sys
from pathlib import Path
from typing import Any


class RecipeNotFound(Exception):
    pass


class Recipe:
    default_project: str
    default_build_server: str
    projects: dict[Any]
    build_servers: list[str]

    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)

    def load(self):
        recipe_file_path = self.base_path / 'recipe.py'

        if not recipe_file_path.is_file():
            raise RecipeNotFound(f'Recipe file not found in {self.base_path}')

        module_name = 'recipe'

        sys.path.insert(0, recipe_file_path.parent.as_posix())
        recipe = importlib.import_module(module_name)

        self._update(vars(recipe))

    def _update(self, settings):
        for key in self.__annotations__.keys():
            try:
                value = settings[key]
            except KeyError:
                # TODO: add separate validation
                value = None
            setattr(self, key, value)
