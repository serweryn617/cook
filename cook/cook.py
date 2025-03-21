from .configuration import BuildType, Configuration
from .executors import LocalExecutor, RemoteExecutor
from .library.logger import log
from .rsync import Rsync


class Cook:
    def __init__(self, recipe, configuration, dry_run=False):
        self.recipe = recipe
        self.configuration = configuration
        self.dry_run = dry_run

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
        executable = self.configuration.get_executable()

        if build_steps:
            executor = LocalExecutor('local', self.dry_run, executable)
            executor.run_multiple(build_steps)

    def _remote_build(self):
        build_steps = self.configuration.get_build_steps()
        local_base, remote_base = self.configuration.get_base_paths()
        files_to_send = self.configuration.get_files_to_send()
        files_to_receive = self.configuration.get_files_to_receive()

        setup_rsync = files_to_send or files_to_receive
        if setup_rsync:
            rsync = Rsync(self.build_server, local_base, remote_base, self.dry_run)

        if files_to_send:
            log('Sending Files', 'log')
            rsync.send(files_to_send)

        if build_steps:
            executor = RemoteExecutor(self.build_server, self.dry_run)
            executor.run_multiple(build_steps)

        if files_to_receive:
            log('Receiving Files', 'log')
            rsync.receive(files_to_receive)

    def _composite_build(self):
        components = self.configuration.get_components()

        log('Running Composite Build', 'log')

        for component in components:
            log(f'Component: {component}', 'log')
            self._run_component(component)

    def _run_component(self, component):
        try:
            sub_configuration = Configuration(self.recipe)
            sub_configuration.setup(component, self.build_server)

            sub_cook = Cook(self.recipe, sub_configuration, self.dry_run)
            sub_cook.cook()
        except Exception as e:
            log(f'Component {component} failed!', 'error')
            raise e
