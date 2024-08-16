import shlex
import subprocess


class ProcessRunner:
    def run(self, command, workdir=None):
        return subprocess.run(command, cwd=workdir, shell=True)


class SSHProcessRunner:
    def __init__(self, name):
        self.name = name

    def run(self, command, workdir='.'):
        # Don't quote workdir so using special directories is allowed (e.g. ~)
        command = shlex.quote(f'cd {workdir} && {command}')
        command = f'ssh {self.name} {command}'
        return subprocess.run(command, shell=True)
