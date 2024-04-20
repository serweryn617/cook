import subprocess

import fabric

from .configuration import BuildType, Configuration
from .executors import LocalExecutor, RemoteExecutor
from .rsync import Rsync


class Cook:
    def __init__(self, recipe, configuration, logger):
        self.recipe = recipe
        self.configuration = configuration
        self.logger = logger

    def cook(self):
        build_type = self.configuration.get_build_type()
        self.build_server = self.configuration.get_build_server()

        if build_type == BuildType.LOCAL:
            self._local_build()
        elif build_type == BuildType.COMPOSITE:
            self._composite_build()
        elif build_type == BuildType.REMOTE:
            self._remote_build()
        else:
            raise RuntimeError(f'Unknown build type: {build_type}')

    def _local_build(self):
        build_steps = self.configuration.get_build_steps()

        if build_steps:
            self.logger.print('local', 'Running local build')
            executor = LocalExecutor('local', self.logger)
            executor.run_multiple(build_steps)

    def _remote_build(self):
        build_steps = self.configuration.get_build_steps()
        local_base, remote_base = self.configuration.get_base_paths()
        files_to_send = self.configuration.get_files_to_send()
        files_to_receive = self.configuration.get_files_to_receive()

        setup_rsync = files_to_send or files_to_receive
        if setup_rsync:
            rsync = Rsync(self.build_server, local_base, remote_base, self.logger)

        if files_to_send:
            self.logger.print('remote', 'Sending Files')
            rsync.send(files_to_send)

        if build_steps:
            self.logger.print('remote', 'Running Remote Build')
            executor = RemoteExecutor(self.build_server, self.logger)
            executor.run_multiple(build_steps)

        if files_to_receive:
            self.logger.print('remote', 'Receiving Files')
            rsync.receive(files_to_receive)

    def _composite_build(self):
        components = self.configuration.get_components()

        if not components:  # TODO required?
            return

        self.logger.print('local', 'Executing Components')

        for component in components:
            self.logger.print('local', f'Component: {component}')
            self._run_component(component)

    def _run_component(self, component):
        try:
            sub_configuration = Configuration(self.recipe)
            sub_configuration.setup(component, self.build_server)

            sub_cook = Cook(self.recipe, sub_configuration, self.logger)
            sub_cook.cook()
        except Exception as e:
            self.logger.print('error', f'Component {component} failed!')
            raise e
