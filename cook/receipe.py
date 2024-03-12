import importlib.util
import sys
from pathlib import Path


class Receipe:
    def __init__(self, base_path: Path):
        self.base_path = base_path

        self.projects = None

        self.default_project = None
        self.default_build_server = 'local'

    def load(self):
        p = self.base_path.glob('**/receipe.py')
        p = str(list(p)[0])

        module_name, file_path = 'receipe', p

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        receipe = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = receipe
        spec.loader.exec_module(receipe)

        if hasattr(receipe, 'projects'):
            self.projects = receipe.projects
        else:
            assert False, 'No projects found in receipe.'

        if hasattr(receipe, 'default_project'):
            self.default_project = receipe.default_project

        if hasattr(receipe, 'default_build_server'):
            self.default_build_server = receipe.default_build_server

    def validate():
        # TODO
        ...