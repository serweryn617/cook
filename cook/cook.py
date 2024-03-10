import fabric
import subprocess

from .rsync import Rsync
from .receipe import Receipe
from .configuration import Configuration, BuildType

from rich import print as rprint


GREEN = '[#00cc52]'
PURPLE = '[#d849ff]'
RED = '[#ff0000]'


class Cook:
    def __init__(self, receipe, configuration):
        self.receipe = receipe
        self.configuration = configuration

    def cook(self):
        build_type = self.configuration.get_build_type()

        if build_type == BuildType.LOCAL:
            self._local_build()
        elif build_type == BuildType.COMPOSITE:
            self._composite_build()
        elif build_type == BuildType.REMOTE:
            self._remote_build()
        else:
            raise RuntimeError(f"Unknown build type: {build_type}")

    def _local_build(self):
        build_steps = self.configuration.get_build_steps()
        if build_steps:
            rprint(GREEN + '=== Running local build ===')
            self._execute_steps_local(build_steps)

    def _execute_steps_local(self, steps):
        for workdir, command in steps:
            rprint(GREEN + f'=== Workdir/Command: {workdir}: {command} ===')

            try:
                subprocess.run(command, cwd=workdir, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                return_code = e.returncode
                rprint(RED + f'Encountered non-zero exit code: {return_code}')
                exit(return_code)

    def _remote_build(self):
        ssh_name = self.configuration.get_server_ssh_name()
        project_remote_build_path = self.configuration.get_project_remote_build_path()
        project_path = self.configuration.get_project_path()
        rsync = Rsync(project_path, ssh_name, project_remote_build_path)

        files_to_send = self.configuration.get_files_to_send()
        files_to_exclude = self.configuration.get_files_to_exclude()
        if files_to_send:
            self._send_files(rsync, files_to_send, files_to_exclude)

        build_steps = self.configuration.get_build_steps()
        if build_steps:
            rprint(PURPLE + '=== Running Remote Build ===')
            self._run_build_steps(ssh_name, build_steps)

        files_to_receive = self.configuration.get_files_to_receive()
        if files_to_receive:
            self._receive_files(rsync, files_to_receive)

    def _send_files(self, rsync, files_to_send, files_to_exclude):
        rprint(GREEN + '=== Sending Files ===')
        rsync.send(files_to_send, files_to_exclude)

    def _receive_files(self, rsync, files_to_receive):
        rprint(GREEN + '=== Receiving Files ===')
        rsync.receive(files_to_receive)

    def _run_build_steps(self, ssh_name, build_steps):
        with fabric.Connection(ssh_name) as c:
            for workdir, command in build_steps:
                rprint(PURPLE + f'=== Workdir/Command: {workdir}: {command} ===')

                with c.cd(workdir):
                    result = c.run(command, warn=True)

                return_code = result.return_code
                if return_code != 0:
                    rprint(RED + f'Encountered non-zero exit code: {return_code}')
                    exit(return_code)

    def _composite_build(self):
        components = self.configuration.get_components()
        if not components:
            return
        
        rprint(GREEN + '=== Executing Components ===')
        for component in components:
            rprint(GREEN + f'=== Running Component: {component} ===')
            
            sub_configuration = Configuration(self.receipe)
            
            build_server = self.configuration.get_build_server()
            sub_configuration.setup(component, build_server)

            sub_cook = Cook(self.receipe, sub_configuration)
            sub_cook.cook()