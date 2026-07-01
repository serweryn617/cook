from collections.abc import Sequence
from pathlib import Path


class BuildStep:
    def __init__(
        self,
        *,
        workdir: str | Path = ".",
        command: str = "",
        expected_return_code: int = 0,
        check: bool = True,
    ) -> None:
        self.command = command
        self.workdir = workdir
        self.expected_return_code = expected_return_code
        self.check = check


type Commands = Sequence[str]
type WorkdirCommands = Sequence[Sequence[str]]
type ClassSteps = Sequence[BuildStep]

type BuildSteps = Commands | WorkdirCommands | ClassSteps

def convert_build_steps(
    steps: BuildSteps,
) -> list[BuildStep]:
    step_objects: list[BuildStep] = []

    for step in steps:
        if isinstance(step, BuildStep):
            step_objects.append(step)
        elif isinstance(step, str):
            step_objects.append(BuildStep(command=step))
        elif isinstance(step, (list, tuple)) and len(step) == 2 and isinstance(step[0], str) and isinstance(step[1], str):  # type: ignore
            step_objects.append(BuildStep(workdir=step[0], command=step[1]))
        else:
            raise RuntimeError(step, "should be string or list/tuple of 2 strings")

    return step_objects
