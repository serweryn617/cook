import subprocess
from socket import gaierror

import fabric
import invoke

from .exception import ProcessError
from .watchers import RichPrinter


class ExecutorError(Exception):
    def __init__(self, message, name, return_code):
        super().__init__(message)
        self.name = name
        self.return_code = return_code


class Executor:
    def __init__(self, name=None, logger=None, rich_output=False):
        self.name = name
        self.logger = logger
        self.rich_output = rich_output

    def run(self, context, workdir, command, responders):
        run_args = {'watchers': []}

        if self.rich_output:
            rich_printer = RichPrinter(self.logger)
            run_args['hide'] = 'both'
            run_args['watchers'].append(rich_printer)

        if responders:
            run_args['watchers'].extend(responders)

        try:
            with context.cd(workdir):
                result = context.run(command, warn=True, pty=True, **run_args)
        except gaierror as e:
            raise ExecutorError(e.strerror, self.name, e.errno)

        return_code = result.return_code
        if return_code != 0:
            raise ProcessError(f'Encountered non-zero exit code: {return_code}', return_code)


class LocalExecutor(Executor):
    def run_multiple(self, steps):
        context = invoke.context.Context()
        for step in steps:
            if self.logger:
                self.logger.local(f'Local Workdir/Command: {step.workdir}: {step.command}')

            self.run(context, step.workdir, step.command, step.responders)


class RemoteExecutor(Executor):
    def run_multiple(self, steps):
        with fabric.Connection(self.name) as context:
            for step in steps:
                if self.logger:
                    self.logger.remote(f'Remote Workdir/Command: {self.name}:{step.workdir}: {step.command}')

                self.run(context, step.workdir, step.command, step.responders)
