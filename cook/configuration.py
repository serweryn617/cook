from enum import Enum, auto
from pathlib import Path


class BuildType(Enum):
    LOCAL = auto()
    REMOTE = auto()
    COMPOSITE = auto()


class Configuration:
    def __init__(self, receipe):
        self.projects = receipe.projects

        self.default_project = receipe.default_project
        self.default_build_server = receipe.default_build_server

        self.base_path = receipe.base_path
        self.skip = False

    def setup(self, project, server):
        if project is None:
            project = self.default_project
        self._set_project(project)

        server_override = self._get_build_server_override()
        if server_override is not None:
            server = server_override

        if server is None:
            server = self.default_build_server
        self._set_build_server(server)

    def _set_project(self, project):
        assert project in self.projects, f'No such project {project}'

        self.project = project

        self.source_files_location = '.'
        if (
            'build_servers' in self.projects[self.project] and
            'local' in self.projects[self.project]['build_servers'] and
            'base_path' in self.projects[self.project]['build_servers']['local']
        ):
            self.source_files_location = self.projects[self.project]['build_servers']['local']['base_path']

    def _set_build_server(self, build_server):
        self.build_server = build_server

        if self._is_composite():
            return

        build_servers = self.projects[self.project]['build_servers']
        assert build_server in build_servers, f'Build server {build_server} not defined for {self.project}'

        if 'skip' in build_servers[build_server] and build_servers[build_server]['skip'] == True:
            self.skip = True
            return

        assert 'base_path' in build_servers[build_server], f"No base_path defined for {self.project} on build server {build_server}"
        self.remote_build_path = build_servers[build_server]['base_path']

    def _get_build_server_override(self):
        if 'build_servers' not in self.projects[self.project]:
            return None

        server_configs = self.projects[self.project]['build_servers']
        for server_name, config in server_configs.items():
            if 'override' in config and config['override'] == True:
                return server_name

    def _is_composite(self):
        return 'components' in self.projects[self.project]

    def get_build_type(self):
        build_type = BuildType.REMOTE

        if self._is_composite():
            build_type = BuildType.COMPOSITE
        elif self.build_server == 'local':
            build_type = BuildType.LOCAL

        return build_type

    def get_build_server(self):
        return self.build_server

    def get_server_ssh_name(self):
        # TODO: Used?
        if self.build_server == 'local':
            return None

        return self.build_server

    def get_project_remote_build_path(self):
        if self.build_server == 'local':
            return None

        # TODO: better handle this
        if (
            'build_servers' in self.projects[self.project] and
            self.build_server in self.projects[self.project]['build_servers'] and
            'base_path' in self.projects[self.project]['build_servers'][self.build_server]
        ):
            return self.projects[self.project]['build_servers'][self.build_server]['base_path']

    def get_source_files_path(self):
        return self.base_path / self.source_files_location

    def get_files_to_send(self):
        send_step = 'send' in self.projects[self.project]

        if not send_step or self.build_server == 'local':
            return None

        base_dir = self.base_path / self.source_files_location
        files_to_send = [base_dir / file_dir for file_dir in self.projects[self.project]['send']]
        return [str(file) for file in files_to_send]

    def get_files_to_exclude(self):
        if 'exclude' not in self.projects[self.project] or self.build_server == 'local':
            return None

        return self.projects[self.project]['exclude']

    def get_files_to_receive(self):
        if 'receive' not in self.projects[self.project] or self.build_server == 'local':
            return None

        base_dir = Path(self.remote_build_path)
        files_to_receive = [base_dir / file_dir for file_dir in self.projects[self.project]['receive']]
        return [str(file) for file in files_to_receive]

    def get_build_steps(self):
        if 'build_steps' not in self.projects[self.project]:
            return None

        if self.build_server == 'local':
            base_dir = self.base_path / self.source_files_location
        else:
            base_dir = Path(self.remote_build_path)

        build_steps = []
        for step in self.projects[self.project]['build_steps']:
            if isinstance(step, tuple):
                workdir, command = step
            else:
                workdir = '.'
                command = step

            build_steps.append((base_dir / workdir, command))

        return build_steps

    def get_components(self):
        if 'components' not in self.projects[self.project]:
            return None

        return self.projects[self.project]['components']