class BuildStep:
    def __init__(self, workdir='.', command='', expected_return_code=0, check=True):
        self.command = command
        self.workdir = workdir
        self.expected_return_code = expected_return_code
        self.check = check


def convert_build_steps(steps):
    step_objects = []

    for step in steps:
        if isinstance(step, BuildStep):
            step_objects.append(step)
        elif isinstance(step, str):
            step_objects.append(BuildStep(command=step))
        elif isinstance(step, (list, tuple)) and len(step) == 2 and isinstance(step[0], str) and isinstance(step[1], str):
            step_objects.append(BuildStep(workdir=step[0], command=step[1]))
        else:
            raise RuntimeError(step, "should be string or list/tuple of 2 strings")

    return step_objects