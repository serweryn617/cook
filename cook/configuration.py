from enum import Enum, auto
from pathlib import Path


class BuildType(Enum):
    LOCAL = auto()
    REMOTE = auto()
    COMPOSITE = auto()


class Configuration:
    def __init__(self, receipe):
        self.projects = receipe.projects
        self.build_servers = receipe.build_servers

        self.default_project = receipe.default_project
        self.default_build_server = receipe.default_build_server

        self.base_path = receipe.base_path

    def setup(self, project, server):
        if project is not None:
            self._set_project(project)
        else:
            self._set_project(self.default_project)

        if 'build_server' in self.projects[self.project]:
            server = self.projects[self.project]['build_server']

        if server is not None:
            self._set_build_server(server)
        else:
            self._set_build_server(self.default_build_server)

    def _set_project(self, project):
        assert project in self.projects, f'No such project {project}'

        self.project = project

        self.location = '.'
        if 'location' in self.projects[self.project]:
            self.location = self.projects[self.project]['location']

    def _set_build_server(self, build_server):
        assert build_server in self.build_servers or build_server == 'local', f'Unknown build server: {build_server}'

        if build_server != 'local' and not self._is_composite():
            assert 'ssh_name' in self.build_servers[build_server]
            assert self.project in self.build_servers[build_server]['project_remote_build_paths'], f"{self.project}, {self.build_servers}"
            self.remote_build_path = self.build_servers[build_server]['project_remote_build_paths'][self.project]

        self.build_server = build_server

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
        if self.build_server == 'local':
            return None

        return self.build_servers[self.build_server]['ssh_name']

    def get_project_remote_build_path(self):
        if self.build_server == 'local':
            return None

        # TODO: better handle this
        if self.project not in self.build_servers[self.build_server]['project_remote_build_paths']:
            return None

        return self.build_servers[self.build_server]['project_remote_build_paths'][self.project]

    def get_project_path(self):
        return self.base_path / self.location

    def get_files_to_send(self):
        if 'send' not in self.projects[self.project] or self.build_server == 'local':
            return None

        base_dir = self.base_path / self.location
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
            base_dir = self.base_path / self.location
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