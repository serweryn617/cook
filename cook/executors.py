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

    def run(self, context, step):
        run_args = {'watchers': []}

        if self.rich_output and self.logger:
            rich_printer = RichPrinter(self.logger)
            run_args['hide'] = 'both'
            run_args['watchers'].append(rich_printer)

        if step.responders:
            run_args['watchers'].extend(step.responders)

        with context.cd(step.workdir):
            result = context.run(step.command, warn=True, pty=True, **run_args)

        return_code = result.return_code
        if step.check and return_code != step.expected_return_code:
            raise ProcessError(f'Encountered unexpected exit code {return_code}, expected {step.expected_return_code}', return_code)


class LocalExecutor(Executor):
    def run_multiple(self, steps):
        context = invoke.context.Context()
        for step in steps:
            if self.logger:
                self.logger.print('local', f'Local Workdir/Command: {step.workdir}: {step.command}')

            self.run(context, step)


class RemoteExecutor(Executor):
    def _execute_step(self, context, step):
        if self.logger:
            self.logger.print('remote', f'Remote Workdir/Command: {self.name}:{step.workdir}: {step.command}')

        try:
            self.run(context, step)
        except gaierror as e:
            raise ExecutorError(e.strerror, self.name, e.errno)

    def run_multiple(self, steps):
        with fabric.Connection(self.name) as context:
            for step in steps:
                self._execute_step(context, step)
