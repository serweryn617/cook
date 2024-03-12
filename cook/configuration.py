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

    def _get_nested_item(self, source_dict, *keys):
        nested_item = source_dict
        for key in keys:
            if key not in nested_item:
                return None
            nested_item = nested_item[key]
        return nested_item

    def _set_project(self, project):
        project_defined = project in self.projects
        assert project_defined, f'No such project {project}'

        self.project = project

    def _set_build_server(self, build_server):
        self.build_server = build_server

        if self._is_composite():
            return

        assert 'build_servers' in self.projects[self.project], f'Build servers not defined for {self.project}'
        build_servers = self.projects[self.project]['build_servers']
        assert build_server in build_servers, f'Build server {build_server} not defined for {self.project}'

        if 'skip' in build_servers[build_server] and build_servers[build_server]['skip'] == True:
            self.skip = True
            return

        assert 'build_path' in build_servers[build_server], f"No base_path defined for {self.project} on build server {build_server}"
        self.remote_path = Path(build_servers[build_server]['build_path'])

        local_path = self._get_nested_item(build_servers, 'local', 'build_path')
        if local_path is not None:
            self.local_path = Path(local_path)

    def _get_build_server_override(self):
        if 'build_servers' not in self.projects[self.project]:
            return None

        server_configs = self.projects[self.project]['build_servers']
        for server_name, config in server_configs.items():
            if 'override' in config and config['override'] == True:
                return server_name

    def _is_composite(self):
        is_composite = 'components' in self.projects[self.project]
        return is_composite

    def _is_local(self):
        is_local = self.build_server == 'local'
        return is_local

    def get_build_type(self):
        if self._is_composite():
            build_type = BuildType.COMPOSITE
        elif self._is_local():
            build_type = BuildType.LOCAL
        else:
            build_type = BuildType.REMOTE

        return build_type

    def get_build_server(self):
        return self.build_server

    def get_project_remote_path(self):
        if self.build_server == 'local':
            return None

        # TODO: better handle this
        if (
            'build_servers' in self.projects[self.project] and
            self.build_server in self.projects[self.project]['build_servers'] and
            'build_path' in self.projects[self.project]['build_servers'][self.build_server]
        ):
            return self.projects[self.project]['build_servers'][self.build_server]['build_path']

    def get_source_files_path(self):
        return self.base_path / self.local_path

    def get_files_to_send(self):
        files_to_send = 'send' in self.projects[self.project]

        if not files_to_send:
            return None

        base_dir = self.base_path / self.local_path
        files_to_send = [base_dir / file_dir for file_dir in self.projects[self.project]['send']]
        return [str(file) for file in files_to_send]

    def get_files_to_exclude(self):
        files_to_exclude = 'exclude' in self.projects[self.project]

        if not files_to_exclude:
            return None

        return self.projects[self.project]['exclude']

    def get_files_to_receive(self):
        files_to_receive = 'receive' in self.projects[self.project]

        if not files_to_receive:
            return None

        base_dir = self.remote_path
        files_to_receive = [base_dir / file_dir for file_dir in self.projects[self.project]['receive']]

        return [str(file) for file in files_to_receive]

    def _get_build_steps_base_dir(self):
        if self._is_local():
            if self.local_path.is_absolute():
                base_dir = self.local_path
            else:
                base_dir = self.base_path / self.local_path
        else:
            base_dir = self.remote_path
        return base_dir

    def get_build_steps(self):
        build_steps_defined = 'build_steps' in self.projects[self.project]

        if not build_steps_defined:
            return None

        build_steps = []
        base_dir = self._get_build_steps_base_dir()

        for step in self.projects[self.project]['build_steps']:
            if isinstance(step, tuple):
                workdir, command = step
            else:
                workdir = '.'
                command = step

            build_steps.append((base_dir / workdir, command))

        return build_steps

    def get_components(self):
        components_defined = 'components' in self.projects[self.project]

        if not components_defined:
            return None

        return self.projects[self.project]['components']