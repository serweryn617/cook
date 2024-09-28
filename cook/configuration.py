from copy import copy
from enum import Enum, auto
from pathlib import Path
from typing import Any

from .build import BuildServer, BuildStep, LocalBuildServer


def build_steps_from_list(steps):
    step_objects = []

    for step in steps:
        if isinstance(step, BuildStep):
            step_objects.append(step)
        elif isinstance(step, str):
            step_objects.append(BuildStep(command=step))
        elif isinstance(step, (list, tuple)) and len(step) == 2 and isinstance(step[0], str) and isinstance(step[1], str):
            step_objects.append(BuildStep(workdir=step[0], command=step[1]))
        else:
            raise RuntimeError(step, "should be string or list/tuple of 2 strings")

    return step_objects


def local_build_from_list(steps):
    return {
        'build_servers': [
            LocalBuildServer(),
        ],
        'build_steps': build_steps_from_list(steps),
    }


def get_nested_item(source_dict, *keys, default=None):
    nested_item = source_dict
    for key in keys:
        if key not in nested_item:
            return default
        nested_item = nested_item[key]
    return nested_item


class ConfigurationError(Exception):
    pass


class BuildType(Enum):
    LOCAL = auto()
    REMOTE = auto()
    COMPOSITE = auto()


class Configuration:
    def __init__(self, recipe):
        self.projects = self._preprocess_projects(recipe.projects)
        self.build_servers = self._preprocess_build_servers()

        self.default_project = recipe.default_project
        self.default_build_server = recipe.default_build_server

        self.base_path = recipe.base_path
        self.skip = False

    def setup(self, project=None, server=None):
        if project is None:
            project = self.default_project
        if project is None:
            raise ConfigurationError('No project selected!')

        if server is None:
            server = self.default_build_server
        if server is None:
            raise ConfigurationError('No build server selected!')

        self._set_project(project)
        self._set_build_server(server)

        if not self._is_composite():
            self._update_paths()

        # TODO: validate recipe contents and print warnings

    def _preprocess_projects(self, projects: dict[Any]):
        # TODO: move preprocessing to Model class and create generic config model
        preprocessed_projects = {}

        for name, definition in projects.items():
            if isinstance(definition, dict):
                build_steps = get_nested_item(definition, 'build_steps')
                if build_steps is not None and isinstance(build_steps, (list, tuple)):
                    definition['build_steps'] = build_steps_from_list(build_steps)
            elif isinstance(definition, (list, tuple)):
                definition = local_build_from_list(definition)
            else:
                raise ConfigurationError('Unknown project format!')

            preprocessed_projects[name] = definition

        return preprocessed_projects

    def _preprocess_build_servers(self):
        build_servers = set()
        for name, project in self.projects.items():
            if 'build_servers' not in project:
                raise ConfigurationError(f'Build servers list not defined for project {name}')
            build_servers.update([b.name for b in project['build_servers']])

        build_servers = sorted(build_servers)
        if 'local' in build_servers:
            build_servers.remove('local')
            build_servers.insert(0, 'local')

        return build_servers

    def _set_project(self, project):
        project_defined = project in self.projects

        if not project_defined:
            raise ConfigurationError(f'No such project {project}')

        self.project = project

    def _set_build_server(self, build_server_name):
        server_override = self._get_build_server_override()
        if server_override is not None:
            build_server_name = server_override

        if self._is_composite():
            self.build_server = BuildServer(name=build_server_name)
            return

        for build_server in get_nested_item(self.projects, self.project, 'build_servers'):
            if build_server.name == build_server_name:
                self.build_server = build_server
                break
        else:
            raise ConfigurationError(f'Build server {build_server_name} not defined for {self.project}')

        if self.build_server.skip == True:
            self.skip = True

    def _get_build_server_override(self):
        build_servers = get_nested_item(self.projects, self.project, 'build_servers')
        if build_servers is None:
            return None

        overrides = []
        for build_server in build_servers:
            if build_server.override == True:
                overrides.append(build_server.name)

        if len(overrides) > 1:
            raise ConfigurationError(f'Multiple server overrides defined for {self.project}')

        if overrides:
            return overrides[0]

    def _update_paths(self):
        if self.build_server.build_path is None:
            raise ConfigurationError(f'No build path defined for {self.project} on build server {build_server.name}')

        build_path = Path(self.build_server.build_path)
        if self._is_local() and not build_path.is_absolute():
            self.build_path = (self.base_path / build_path).resolve()
        else:
            self.build_path = build_path

    def _is_composite(self):
        is_composite = 'components' in self.projects[self.project]
        return is_composite

    def _is_local(self):
        return self.build_server.is_local

    def get_build_type(self):
        if self._is_composite():
            build_type = BuildType.COMPOSITE
        elif self._is_local():
            build_type = BuildType.LOCAL
        else:
            build_type = BuildType.REMOTE

        return build_type

    def get_build_server(self):
        return self.build_server.name

    def get_base_paths(self):
        return self.base_path.as_posix(), self.build_path.as_posix()

    def get_files_to_send(self):
        if self.skip == True:
            return None

        return get_nested_item(self.projects, self.project, 'send')

    def get_files_to_receive(self):
        if self.skip == True:
            return None

        return get_nested_item(self.projects, self.project, 'receive')

    def get_build_steps(self):
        if self.skip == True:
            return None

        build_steps = get_nested_item(self.projects, self.project, 'build_steps')

        if build_steps is None:
            return None

        parsed_build_steps = []

        for step in build_steps:
            # shallow copy is enough as only a str is modified but be careful
            parsed_step = copy(step)
            parsed_step.workdir = self.build_path / parsed_step.workdir
            parsed_build_steps.append(parsed_step)

        return parsed_build_steps

    def get_components(self):
        components = get_nested_item(self.projects, self.project, 'components')
        return components
