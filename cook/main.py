from .configuration import Configuration, ConfigurationError
from .cook import Cook
from .exception import ProcessError
from .executors import ExecutorError
from .logger import Logger
from .recipe import Recipe, RecipeError, RecipeNotFound


def print_targets(recipe: Recipe):
    print(f'Projects defined in {recipe.base_path / "recipe.py"}:')
    for key in recipe.projects.keys():
        print('  ' + key, '<- default' if key == recipe.default_project else '')


# TODO: create class
def main(recipe_base_path, project, build_server, rich_output=False, quiet=False, dry_run=False, list_targets=False):
    logger = Logger(rich_output, quiet)

    try:
        recipe = Recipe(recipe_base_path)
        recipe.load()
        
        if list_targets:
            print_targets(recipe)
            return

        configuration = Configuration(recipe)
        configuration.setup(project, build_server)

        cook = Cook(recipe, configuration, logger)
        cook.set_dry_run(dry_run)
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
