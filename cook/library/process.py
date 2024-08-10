import subprocess
import shlex


class ProcessRunner:
    def run(self, command, workdir=None):
        return subprocess.run(command, cwd=workdir, shell=True)


class SSHProcessRunner:
    def __init__(self, name):
        self.name = name

    def run(self, command, workdir=None):
        command = shlex.quote(f'cd {workdir} && {command}')
        command = f'ssh {self.name} {command}'
        return subprocess.run(command, shell=True)