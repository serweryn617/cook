import sys

import pytest

from cook.recipe import Recipe

TEST_RECIPE = '''
default_project = 'build'
default_build_server = 'remote'
projects = {'build': 'test'}
unknown_field = 'content'
'''


@pytest.fixture
def tmp_recipe(tmp_path):
    recipe_file = tmp_path / "recipe.py"
    recipe_file.write_text(TEST_RECIPE, encoding="utf-8")
    return tmp_path


@pytest.fixture
def restore_sys_path():
    original = sys.path.copy()
    yield
    sys.path = original


def test_recipe_is_loaded(tmp_recipe, restore_sys_path):
    recipe = Recipe(tmp_recipe)
    recipe.load()

    assert recipe.default_project == 'build'
    assert recipe.default_build_server == 'remote'
    assert recipe.projects == {'build': 'test'}
    assert not hasattr(recipe, 'unknown_field')
