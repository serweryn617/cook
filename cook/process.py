import os
import shlex
import shutil
import subprocess
from pathlib import Path

from .exception import ConfigurationError


class ProcessRunner:
    POSIX_EXECUTABLE = "bash"
    NT_EXECUTABLE = "PowerShell"

    def __init__(self, executable: str | None = None) -> None:
        if executable is not None:
            self.executable = shutil.which(executable)
            if self.executable is None:
                raise ConfigurationError(f"Executable not found: {executable}")
            return

        executable = self.POSIX_EXECUTABLE if os.name == "posix" else self.NT_EXECUTABLE

        self.executable = shutil.which(executable)  # if not found default system shell will be used

    def run(self, command: str, workdir: str | Path | None = None):
        return subprocess.run(command, cwd=workdir, shell=True, executable=self.executable)


class SSHProcessRunner:
    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, command: str, workdir: str | Path = "."):
        # Don't quote workdir so using special directories is allowed (e.g. ~)
        command = shlex.quote(f"cd {workdir} && {command}")
        command = f"ssh {self.name} {command}"
        return subprocess.run(command, shell=True)
