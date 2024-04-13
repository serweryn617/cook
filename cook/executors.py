import subprocess

import fabric
import invoke

from .watchers import RichPrinter


class ExecutorProcessError(Exception):
    def __init__(self, message, return_code):
        super().__init__(message)
        self.return_code = return_code


class LocalExecutor:
    def __init__(self, logger=None, rich_output=False):
        self.logger = logger
        self.rich_output = rich_output

    def run(self, workdir, command):
        if self.logger:
            self.logger.local(f'Local Workdir/Command: {workdir}: {command}')

        run_args = {'watchers': []}

        if self.rich_output:
            rich_printer = RichPrinter(self.logger)
            run_args['hide'] = 'both'
            run_args['watchers'].append(rich_printer)

        context = invoke.context.Context()
        with context.cd(workdir):
            result = context.run(command, warn=True, pty=True, **run_args)

        return_code = result.return_code
        if return_code != 0:
            raise ExecutorProcessError(f'Encountered non-zero exit code: {return_code}', return_code)

    def run_multiple(self, steps):
        for step in steps:
            self.run(*step)


class RemoteExecutor:
    def __init__(self, ssh_name, logger=None, rich_output=False):
        self.logger = logger
        self.ssh_name = ssh_name
        self.rich_output = rich_output

    def run(self, context, workdir, command):
        if self.logger:
            self.logger.remote(f'Remote Workdir/Command: {self.ssh_name}:{workdir}: {command}')

        run_args = {'watchers': []}

        if self.rich_output:
            rich_printer = RichPrinter(self.logger)
            run_args['hide'] = 'both'
            run_args['watchers'].append(rich_printer)

        with context.cd(workdir):
            result = context.run(command, warn=True, pty=True, **run_args)

        return_code = result.return_code
        if return_code != 0:
            raise ExecutorProcessError(f'Encountered non-zero exit code: {return_code}', return_code)

    def run_multiple(self, steps):
        with fabric.Connection(self.ssh_name) as context:
            for step in steps:
                self.run(context, *step)
