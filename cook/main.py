from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .executors import ExecutorProcessError
from .logger import Logger
from .recipe import Recipe, RecipeError, RecipeNotFound


def main(settings):
    try:
        recipe = Recipe(settings.recipe_base_path)
        recipe.load()

        configuration = Configuration(recipe)
        configuration.setup(settings.project, settings.build_server)

        cook = Cook(recipe, configuration, settings.rich_output)
        cook.cook()

    except (RecipeNotFound, RecipeError, ConfigurationError) as e:
        Logger().error(e)
        exit(1)

    except ExecutorProcessError as e:
        Logger().error(e)
        exit(e.return_code)
