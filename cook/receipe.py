import importlib.util
import sys
from pathlib import Path
from cook import logger


class Receipe:
    def __init__(self, base_path: Path):
        self.base_path = base_path

        self.projects = None

        self.default_project = None
        self.default_build_server = 'local'

    def load(self):
        receipes = list(self.base_path.glob('receipe.py'))

        if len(receipes) == 0:
            logger.error(f'Receipe file not found in {self.base_path}')
            exit(1)

        receipe_file_path = str(receipes[0])
        module_name = 'receipe'

        spec = importlib.util.spec_from_file_location(module_name, receipe_file_path)
        receipe = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = receipe
        spec.loader.exec_module(receipe)

        if hasattr(receipe, 'projects'):
            self.projects = receipe.projects
        else:
            logger.error('No projects found in receipe.')
            exit(1)

        if hasattr(receipe, 'default_project'):
            self.default_project = receipe.default_project

        if hasattr(receipe, 'default_build_server'):
            self.default_build_server = receipe.default_build_server
