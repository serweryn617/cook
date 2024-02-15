import importlib.util
import sys
from pathlib import Path


class Receipe:
    def __init__(self, base_path):
        self.base_path = base_path

        self.build_server = 'local'

    def load(self):
        p = self.base_path.glob('**/receipe.py')
        p = str(list(p)[0])

        module_name, file_path = 'receipe', p

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        receipe = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = receipe
        spec.loader.exec_module(receipe)

        if hasattr(receipe, 'build_servers'):
            self.build_servers = receipe.build_servers

        if hasattr(receipe, 'projects'):
            self.projects = receipe.projects
        else:
            assert False, 'No projects found in receipe.'

        default_project = list(self.projects.keys())[0]
        if hasattr(receipe, 'default_project'):
            default_project = receipe.default_project
        self.set_project(default_project)

        default_build_server = 'local'
        if hasattr(receipe, 'default_build_server'):
            default_build_server = receipe.default_build_server
        self.set_build_server(default_build_server)

    def set_project(self, project):
        assert project in self.projects, f'No such project {project}'

        self.project = project

        self.location = '.'
        if 'location' in self.projects[self.project]:
            self.location = self.projects[self.project]['location']

    def set_build_server(self, build_server):
        assert build_server in self.build_servers or build_server == 'local', f'Unknown build server: {build_server}'

        if build_server != 'local':
            assert 'ssh_name' in self.build_servers[build_server]
            assert self.project in self.build_servers[build_server]['project_remote_build_paths']
            self.remote_build_path = self.build_servers[build_server]['project_remote_build_paths'][self.project]

        self.build_server = build_server

    def is_build_local(self):
        return self.build_server == 'local'

    def get_server_ssh_name(self):
        if self.build_server == 'local':
            return None

        return self.build_servers[self.build_server]['ssh_name']

    def get_project_remote_build_path(self):
        if self.build_server == 'local':
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

        base_dir = self.base_path / self.location
        files_to_exclude = [base_dir / file_dir for file_dir in self.projects[self.project]['exclude']]
        return [str(file) for file in files_to_exclude]

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
        for workdir, command in self.projects[self.project]['build_steps']:
            build_steps.append((base_dir / workdir, command))

        return build_steps

    def get_post_actions(self):
        if 'post_actions' not in self.projects[self.project]:
            return None

        base_dir = self.base_path / self.location

        post_actions = []
        for workdir, command in self.projects[self.project]['post_actions']:
            post_actions.append((base_dir / workdir, command))

        return post_actions