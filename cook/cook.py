import fabric
import subprocess

from .rsync import Rsync
from .receipe import Receipe
from .configuration import Configuration, BuildType
from cook import logger


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
            logger.local('=== Running local build ===')
            self._execute_steps_local(build_steps)

    def _execute_steps_local(self, steps):
        for workdir, command in steps:
            logger.local(f'=== Workdir/Command: {workdir}: {command} ===')

            try:
                subprocess.run(command, cwd=workdir, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                return_code = e.returncode
                logger.error(f'Encountered non-zero exit code: {return_code}')
                exit(return_code)

    def _remote_build(self):
        files_to_send = self.configuration.get_files_to_send()
        files_to_exclude = self.configuration.get_files_to_exclude()
        build_steps = self.configuration.get_build_steps()
        files_to_receive = self.configuration.get_files_to_receive()

        ssh_name = self.configuration.get_build_server()

        setup_rsync = files_to_send or files_to_receive

        if setup_rsync:
            source_files_path = self.configuration.get_source_files_path()
            project_remote_path = self.configuration.get_project_build_path()
            rsync = Rsync(source_files_path, ssh_name, project_remote_path)

        if files_to_send:
            logger.remote('=== Sending Files ===')
            rsync.send(files_to_send, files_to_exclude)

        if build_steps:
            logger.remote('=== Running Remote Build ===')
            self._run_build_steps(ssh_name, build_steps)

        if files_to_receive:
            logger.remote('=== Receiving Files ===')
            rsync.receive(files_to_receive)

    def _run_build_steps(self, ssh_name, build_steps):
        with fabric.Connection(ssh_name) as c:
            for workdir, command in build_steps:
                logger.remote(f'=== Workdir/Command: {workdir}: {command} ===')

                with c.cd(workdir):
                    result = c.run(command, warn=True)

                return_code = result.return_code
                if return_code != 0:
                    logger.error(f'Encountered non-zero exit code: {return_code}')
                    exit(return_code)

    def _composite_build(self):
        components = self.configuration.get_components()

        if not components:
            return

        logger.local('=== Executing Components ===')

        for component in components:
            logger.local(f'=== Running Component: {component} ===')

            sub_configuration = Configuration(self.receipe)

            build_server = self.configuration.get_build_server()
            sub_configuration.setup(component, build_server)

            sub_cook = Cook(self.receipe, sub_configuration)
            sub_cook.cook()