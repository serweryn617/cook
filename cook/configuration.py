from enum import Enum, auto
from pathlib import Path
from cook import logger


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
        self._update_local_path()

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
        
        if not project_defined:
            logger.error(f'No such project {project}')
            exit(1)

        self.project = project

    def _set_build_server(self, build_server):
        self.build_server = build_server

        if self._is_composite():
            return

        build_server_config = self._get_nested_item(self.projects, self.project, 'build_servers', build_server)
        if build_server_config is None:
            logger.error(f'Build server {build_server} not defined for {self.project}')
            exit(1)

        skip = self._get_nested_item(build_server_config, 'skip')
        if skip == True:
            self.skip = True
            return

        if not self._is_local():
            remote_path = self._get_nested_item(build_server_config, 'build_path')
            if remote_path is None:
                logger.error(f"No build path defined for {self.project} on build server {build_server}")
                exit(1)
            self.remote_path = Path(remote_path)

    def _update_local_path(self):
        local_path = self._get_nested_item(self.projects, self.project, 'build_servers', 'local', 'build_path')
        if local_path is not None:
            local_path = Path(local_path)
            if local_path.is_absolute():
                self.local_path = local_path
            else:
                self.local_path = self.base_path / local_path

    def _get_build_server_override(self):
        build_servers = self._get_nested_item(self.projects, self.project, 'build_servers')
        if build_servers is None:
            return None

        for server_name, config in build_servers.items():
            override = self._get_nested_item(config, 'override')
            if override == True:
                # TODO: Detect multiple overrides
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

    def get_project_build_path(self):
        build_path = self._get_nested_item(self.projects, self.project, 'build_servers', self.build_server, 'build_path')
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
        if self._is_local():
            base_dir = self.local_path
        else:
            base_dir = self.remote_path
        return base_dir

    def get_build_steps(self):
        if self.skip == True:
            return None

        build_steps = self._get_nested_item(self.projects, self.project, 'build_steps')

        if build_steps is None:
            return None

        parsed_build_steps = []
        base_dir = self._get_build_steps_base_dir()

        for step in build_steps:
            if isinstance(step, tuple):
                workdir, command = step
            else:
                workdir = '.'
                command = step

            parsed_build_steps.append((base_dir / workdir, command))

        return parsed_build_steps

    def get_components(self):
        components = self._get_nested_item(self.projects, self.project, 'components')
        return components