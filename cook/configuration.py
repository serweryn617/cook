from enum import Enum, auto
from pathlib import Path


class ConfigurationError(Exception):
    pass


class BuildType(Enum):
    LOCAL = auto()
    REMOTE = auto()
    COMPOSITE = auto()


class BuildStep:
    def __init__(self, workdir='.', command='', responders=None):
        self.command = command
        self.workdir = workdir

        if responders:
            self.responders = responders
        else:
            self.responders = tuple()


class BuildServer:
    def __init__(self, name, build_path=None, skip=False, override=False, is_local=None):
        self.name = name
        self.build_path = build_path
        self.skip = skip
        self.override = override
        self.is_local = is_local

        if self.is_local is None and name == 'local':
            self.is_local = True
        if self.build_path is None and self.is_local == True:
            self.build_path = '.'


class Configuration:
    def __init__(self, recipe):
        self.projects = recipe.projects

        self.default_project = recipe.default_project
        self.default_build_server = recipe.default_build_server

        self.local_path = recipe.base_path
        self.skip = False

    def setup(self, project=None, server=None):
        if project is None:
            project = self.default_project
        
        if server is None:
            server = self.default_build_server

        self._set_project(project)
        self._set_build_server(server)

        if not self._is_composite():
            self._update_paths()

    def _get_nested_item(self, source_dict, *keys):
        nested_item = source_dict
        for key in keys:
            if key not in nested_item:
                return None
            nested_item = nested_item[key]
        return nested_item

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

        for build_server in self._get_nested_item(self.projects, self.project, 'build_servers'):
            if build_server.name == build_server_name:
                self.build_server = build_server
                break
        else:
            raise ConfigurationError(f'Build server {build_server_name} not defined for {self.project}')

        if self.build_server.skip == True:
            self.skip = True
            return

        remote_path = self.build_server.build_path
        if remote_path is None:
            raise ConfigurationError(f'No build path defined for {self.project} on build server {build_server.name}')

    def _get_build_server_override(self):
        build_servers = self._get_nested_item(self.projects, self.project, 'build_servers')
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
        remote_path = Path(self.build_server.build_path)
        if self._is_local() and not remote_path.is_absolute():
            self.remote_path = self.local_path / remote_path
        else:
            self.remote_path = remote_path

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

    def get_project_build_path(self):
        build_path = self.build_server.build_path
        return build_path

    def get_source_files_path(self):
        return self.local_path

    def get_files_to_send(self):
        files_to_send = self._get_nested_item(self.projects, self.project, 'send')

        if files_to_send is None:
            return None

        files_to_send = [str(self.local_path / file) for file in files_to_send]
        return files_to_send

    def get_files_to_exclude(self):
        files_to_exclude = self._get_nested_item(self.projects, self.project, 'exclude')
        return files_to_exclude

    def get_files_to_receive(self):
        files_to_receive = self._get_nested_item(self.projects, self.project, 'receive')

        if files_to_receive is None:
            return None

        files_to_receive = [str(self.remote_path / file) for file in files_to_receive]
        return files_to_receive

    def _get_build_steps_base_dir(self):
        # breakpoint()
        return self.remote_path

    def get_build_steps(self):
        if self.skip == True:
            return None

        build_steps = self._get_nested_item(self.projects, self.project, 'build_steps')

        if build_steps is None:
            return None

        parsed_build_steps = []
        base_dir = self._get_build_steps_base_dir()

        for step in build_steps:
            if isinstance(step, str):
                workdir = '.'
                command = step
                responders = None
            elif isinstance(step, BuildStep):
                workdir = step.workdir
                command = step.command
                responders = step.responders
            else:
                raise ConfigurationError(f'Expected build step to be of type str of BuildStep, was {type(step)}')

            workdir = base_dir / workdir
            parsed_step = BuildStep(workdir=workdir, command=command, responders=responders)
            parsed_build_steps.append(parsed_step)

        return parsed_build_steps

    def get_components(self):
        components = self._get_nested_item(self.projects, self.project, 'components')
        return components
