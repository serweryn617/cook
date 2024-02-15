import fabric
import subprocess

from .rsync import Rsync
from .receipe import Receipe


class Cook:
    def __init__(self, base_path, project, build_server):
        self.base_path = base_path
        self.project = project
        self.build_server = build_server

    def cook(self):
        self._prepare()

        if self.receipe.is_build_local():
            self._local_build()
        else:
            self._remote_build()

        self._post_actions()

    def _prepare(self):
        self.receipe = Receipe(self.base_path)
        self.receipe.load()

        if self.project is not None:
            self.receipe.set_project(self.project)

        if self.build_server is not None:
            self.receipe.set_build_server(self.build_server)

    def _local_build(self):
        build_steps = self.receipe.get_build_steps()
        if build_steps:
            print('=== Running local build ===')
            self._execute_steps_local(build_steps)

    def _post_actions(self):
        steps = self.receipe.get_post_actions()
        if steps:
            print('=== Running post actions ===')
            self._execute_steps_local(steps)

    def _execute_steps_local(self, steps):
        for workdir, command in steps:
            print(f'=== Workdir: {workdir} === Command: {command} ===')
            subprocess.run(command, cwd=workdir, shell=True)

    def _remote_build(self):
        ssh_name = self.receipe.get_server_ssh_name()
        project_remote_build_path = self.receipe.get_project_remote_build_path()
        project_path = self.receipe.get_project_path()
        rsync = Rsync(project_path, ssh_name, project_remote_build_path)

        files_to_send = self.receipe.get_files_to_send()
        files_to_exclude = self.receipe.get_files_to_exclude()
        if files_to_send:
            self._create_remote_workspace(ssh_name, project_remote_build_path)
            self._send_files(rsync, files_to_send, files_to_exclude)

        build_steps = self.receipe.get_build_steps()
        if build_steps:
            self._run_build_steps(ssh_name, build_steps)

        files_to_receive = self.receipe.get_files_to_receive()
        if files_to_receive:
            self._receive_files(rsync, files_to_receive)

    def _create_remote_workspace(self, ssh_name, remote_build_path):
        print('=== Creating remote project directory ===')
        mkdir_cmd = ['mkdir', '-p', remote_build_path]
        with fabric.Connection(ssh_name) as c:
            c.run(' '.join(mkdir_cmd))

    def _send_files(self, rsync, files_to_send, files_to_exclude):
        print('=== Sending files ===')
        rsync.send(files_to_send, files_to_exclude)

    def _receive_files(self, rsync, files_to_receive):
        print('=== Receiving files ===')
        rsync.receive(files_to_receive)

    def _run_build_steps(self, ssh_name, build_steps):
        with fabric.Connection(ssh_name) as c:
            for workdir, command in build_steps:
                print(f'=== Workdir: {workdir} === Command: {command} ===')
                with c.cd(workdir):
                    res = c.run(command)
                print('Return code:', res)