import pytest

from cook.configuration import Configuration, BuildType
from cook.build import LocalBuildServer, RemoteBuildServer, BuildStep
from cook.sync import SyncFile

from pathlib import Path


# get_build_type
# get_build_server
# get_base_paths
# get_files_to_send
# get_files_to_receive
# get_build_steps
# get_components


class MockRecipe:
    def __init__(self):
        self.default_project = 'build'
        self.default_build_server = 'local'
        self.build_servers = ['local', 'remote']
        self.projects = {
            'build': {
                'build_servers': [
                    LocalBuildServer(),
                    RemoteBuildServer('remote', '/remote/path'),
                ],
                'send': [
                    SyncFile('test/input/file'),
                ],
                'build_steps': [
                    BuildStep(command='cwd test command'),
                    BuildStep(workdir='work', command='test command'),
                    BuildStep(workdir='/work', command='absolute test command'),
                ],
                'receive': [
                    SyncFile('test/output/file'),
                ],
            },
        }
        self.base_path = Path('/recipe/path')


def test_configuration_basic():
    mock_recipe = MockRecipe()
    configuration = Configuration(mock_recipe)
    configuration.setup()

    assert configuration.get_build_type() == BuildType.LOCAL
    assert configuration.get_build_server() == 'local'
    assert configuration.get_base_paths() == ('/recipe/path', '/recipe/path')
    assert configuration.get_files_to_send() == mock_recipe.projects['build']['send']
    assert configuration.get_files_to_receive() == mock_recipe.projects['build']['receive']
    assert configuration.get_components() == None

    # build step workdir is parsed
    build_steps = configuration.get_build_steps()
    assert len(build_steps) == 3
    assert build_steps[0].workdir.as_posix() == '/recipe/path'
    assert build_steps[0].command == 'cwd test command'
    assert build_steps[1].workdir.as_posix() == '/recipe/path/work'
    assert build_steps[1].command == 'test command'
    assert build_steps[2].workdir.as_posix() == '/work'
    assert build_steps[2].command == 'absolute test command'


def test_configuration_remote():
    mock_recipe = MockRecipe()
    configuration = Configuration(mock_recipe)
    configuration.setup(server='remote')

    assert configuration.get_build_type() == BuildType.REMOTE
    assert configuration.get_build_server() == 'remote'
    assert configuration.get_base_paths() == ('/recipe/path', '/remote/path')
    assert configuration.get_files_to_send() == mock_recipe.projects['build']['send']
    assert configuration.get_files_to_receive() == mock_recipe.projects['build']['receive']
    assert configuration.get_components() == None

    # build step remote workdir
    build_steps = configuration.get_build_steps()
    assert len(build_steps) == 3
    assert build_steps[0].workdir.as_posix() == '/remote/path'
    assert build_steps[0].command == 'cwd test command'
    assert build_steps[1].workdir.as_posix() == '/remote/path/work'
    assert build_steps[1].command == 'test command'
    assert build_steps[2].workdir.as_posix() == '/work'
    assert build_steps[2].command == 'absolute test command'


def test_configuration_composite():
    mock_recipe = MockRecipe()
    mock_recipe.projects['composite'] = {
        'components': [
            'build',
            'test',
        ],
    }

    configuration = Configuration(mock_recipe)
    configuration.setup(project='composite')

    assert configuration.get_components() == ['build', 'test']