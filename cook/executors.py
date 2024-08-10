from .exception import ProcessError

# from .watchers import RichPrinter
from .library.process import ProcessRunner, SSHProcessRunner
from .logger import log


class ExecutorError(Exception):
    def __init__(self, message, name, return_code):
        super().__init__(message)
        self.name = name
        self.return_code = return_code


class Executor:
    def __init__(self, name=None):
        self.name = name
        self.dry_run = False

    def set_dry_run(self, dry_run: bool):
        self.dry_run = dry_run

    def run(self, runner, step):
        if self.dry_run:
            return

        # run_args = {'watchers': []}

        # if self.quiet:
        #     run_args['hide'] = 'out'

        # if self.rich_output and self.logger:
        #     rich_printer = RichPrinter(self.logger)
        #     run_args['hide'] = 'both'
        #     run_args['watchers'].append(rich_printer)

        # if step.responders:
        #     run_args['watchers'].extend(step.responders)

        result = runner.run(step.command, workdir=step.workdir)

        return_code = result.returncode
        if step.check and return_code != step.expected_return_code:
            raise ProcessError(f'Encountered unexpected exit code {return_code}, expected {step.expected_return_code}', return_code)


class LocalExecutor(Executor):
    def run_multiple(self, steps):
        runner = ProcessRunner()
        for step in steps:
            log(f'Local Step: {step.workdir}: {step.command}', 'log')

            self.run(runner, step)


class RemoteExecutor(Executor):
    def run_multiple(self, steps):
        runner = SSHProcessRunner(self.name)
        for step in steps:
            log(f'Remote Step: {self.name}:{step.workdir}: {step.command}', 'log')

            self.run(runner, step)
