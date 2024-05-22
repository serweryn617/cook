from unittest.mock import ANY, MagicMock, Mock

import pytest

from cook.build import BuildStep
from cook.executors import Executor


class RichLogger:
    def use_rich_output(self):
        return True

    def is_quiet(self):
        return False


class ContextResult:
    def __init__(self, return_code):
        self.return_code = return_code


class TestExecutor:
    def test_executor_logger(self):
        context = MagicMock()
        context.run = Mock(return_value=ContextResult(0))
        step = BuildStep(workdir='test_dir', command='test_command')

        executor = Executor()
        executor.run(context, step)

        context.cd.assert_called_with('test_dir')
        assert context.run.call_args.args[0] == 'test_command'
        assert context.run.call_args.kwargs['watchers'] == []
