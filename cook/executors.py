import subprocess

import fabric


class ProcessError(Exception):
    def __init__(self, message, return_code):
        super().__init__(message)
        self.return_code = return_code


class LocalExecutor:
    def __init__(self, logger=None):
        self.logger = logger

    def run(self, workdir, command):
        if self.logger:
            self.logger.local(f'Local Workdir/Command: {workdir}: {command}')

        try:
            subprocess.run(command, cwd=workdir, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return_code = e.returncode
            raise ProcessError(f'Encountered non-zero exit code: {return_code}', return_code)

    def run_multiple(self, steps):
        for step in steps:
            self.run(*step)


class RemoteExecutor:
    def __init__(self, ssh_name, logger=None):
        self.logger = logger
        self.ssh_name = ssh_name

    def run(self, context, workdir, command):
        if self.logger:
            self.logger.remote(f'Remote Workdir/Command: {self.ssh_name}:{workdir}: {command}')

        with context.cd(workdir):
            result = context.run(command, warn=True)

        return_code = result.return_code
        if return_code != 0:
            raise ProcessError(f'Encountered non-zero exit code: {return_code}', return_code)

    def run_multiple(self, steps):
        with fabric.Connection(self.ssh_name) as context:
            for step in steps:
                self.run(context, *step)
