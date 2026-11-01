from collections.abc import Callable, Sequence
from inspect import signature
from pathlib import Path

from .context import RecipeContext


class BuildStep:
    def __init__(
        self,
        *,
        workdir: str | Path = ".",
        command: str | Callable[[], str] | Callable[[RecipeContext], str] = "",
        expected_return_code: int = 0,
        check: bool = True,
    ) -> None:
        self.command = command
        self.workdir = workdir
        self.expected_return_code = expected_return_code
        self.check = check


type CommandFactory = Callable[[], str] | Callable[[RecipeContext], str]
type Command = str | CommandFactory
type WorkdirCommand = Sequence[Command]
type BuildStepDefinition = BuildStep | Command | WorkdirCommand
type ClassSteps = Sequence[BuildStep]

type BuildSteps = Sequence[BuildStepDefinition]


def _call_command(command: CommandFactory, context: RecipeContext) -> str:
    try:
        command_signature = signature(command)
    except (TypeError, ValueError):
        return command(context)  # type: ignore

    try:
        command_signature.bind(context)
    except TypeError:
        try:
            command_signature.bind()
        except TypeError as err:
            raise TypeError(
                "Callable build steps must accept either zero arguments or a RecipeContext"
            ) from err
        return command()  # type: ignore

    return command(context)  # type: ignore

class BuildStep:
    def __init__(
        self,
        *,
        workdir: str | Path = ".",
        command: Command = "",
        expected_return_code: int = 0,
        check: bool = True,
    ) -> None:
        self.command = command
        self.workdir = workdir
        self.expected_return_code = expected_return_code
        self.check = check

    def resolve(self, context: RecipeContext) -> str:
        if isinstance(self.command, str):
            return self.command

        command = _call_command(self.command, context)
        if not isinstance(command, str):
            raise RuntimeError("Callable build steps must return a string")

        return command


def convert_build_steps(steps: BuildSteps) -> list[BuildStep]:
    step_objects: list[BuildStep] = []
    for step in steps:
        if isinstance(step, BuildStep):
            step_objects.append(step)
        elif isinstance(step, str):
            step_objects.append(BuildStep(command=step))
        elif callable(step):
            step_objects.append(BuildStep(command=step))
        elif (
            isinstance(step, (list, tuple))
            and len(step) == 2
            and isinstance(step[0], str)
            and (isinstance(step[1], str) or callable(step[1]))
        ):
                step_objects.append(BuildStep(workdir=step[0], command=step[1]))
        else:
            raise RuntimeError(
                step,
                "should be a string, callable, BuildStep, or list/tuple of workdir and command",
            )
    return step_objects
