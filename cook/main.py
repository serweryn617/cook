from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .exception import ProcessError
from .executors import ExecutorError
from .logger import Logger
from .recipe import Recipe, RecipeError, RecipeNotFound


class Settings:
    def __init__(self):
        self.recipe_base_path = None
        self.build_server = None
        self.rich_output = None
        self.project = None
        self.user_args = {}


settings = Settings()


def main():
    global settings

    logger = Logger(settings.rich_output)

    try:
        recipe = Recipe(settings.recipe_base_path)
        recipe.load()

        configuration = Configuration(recipe)
        configuration.setup(settings.project, settings.build_server)

        cook = Cook(recipe, configuration, logger)
        cook.cook()

    except (RecipeNotFound, RecipeError, ConfigurationError) as e:
        logger.print('error', e)
        exit(1)

    except ProcessError as e:
        logger.print('error', e)
        exit(e.return_code)

    except ExecutorError as e:
        logger.print('error', f'{e.name}: {e}')
        exit(e.return_code)
