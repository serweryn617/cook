from unittest.mock import MagicMock, call, patch

import pytest

from cook.build import BuildStep
from cook.exception import ProcessError
from cook.executors import LocalExecutor, RemoteExecutor


@patch('cook.executors.ProcessRunner')
def test_local_executor(MockProcessRunner):
    mock_process_runner = MockProcessRunner.return_value
    mock_process_runner.run.return_value.returncode = 0

    executable = 'shell'
    steps = [
        BuildStep(command='cwd test command'),
        BuildStep(workdir='work', command='test command'),
        BuildStep(workdir='/work', command='absolute test command'),
    ]

    executor = LocalExecutor(executable=executable)
    executor.run_multiple(steps)

    expected_calls = (
        call(
            'cwd test command',
            workdir='.',
        ),
        call(
            'test command',
            workdir='work',
        ),
        call(
            'absolute test command',
            workdir='/work',
        ),
    )

    MockProcessRunner.assert_called_once_with(executable)
    assert mock_process_runner.run.call_count == 3
    mock_process_runner.run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_remote_executor(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    steps = [
        BuildStep(command='cwd test command'),
        BuildStep(workdir='work', command='test command'),
        BuildStep(workdir='/work', command='absolute test command'),
        BuildStep(workdir='"dir with spaces"', command='command with spaces'),
    ]

    executor = RemoteExecutor('remote_host')
    executor.run_multiple(steps)

    expected_calls = (
        call(
            "ssh remote_host 'cd . && cwd test command'",
            shell=True,
        ),
        call(
            "ssh remote_host 'cd work && test command'",
            shell=True,
        ),
        call(
            "ssh remote_host 'cd /work && absolute test command'",
            shell=True,
        ),
        call(
            'ssh remote_host \'cd "dir with spaces" && command with spaces\'',
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 4
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_local_executor_dry_run(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    steps = [
        BuildStep(command='cwd test command'),
    ]

    executor = LocalExecutor(dry_run=True)
    executor.run_multiple(steps)

    assert not mock_subprocess_run.called


@patch('subprocess.run')
def test_remote_executor_dry_run(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    steps = [
        BuildStep(command='cwd test command'),
    ]

    executor = RemoteExecutor('remote_host', dry_run=True)
    executor.run_multiple(steps)

    assert not mock_subprocess_run.called


@patch('cook.executors.ProcessRunner')
def test_local_executor_checks_returncode(MockProcessRunner):
    mock_process_runner = MockProcessRunner.return_value
    mock_process_runner.run.return_value.returncode = 123

    steps = [
        BuildStep(command='cwd test command'),
    ]

    executor = LocalExecutor()

    with pytest.raises(ProcessError) as excinfo:
        executor.run_multiple(steps)

    assert excinfo.value.return_code == 123


@patch('subprocess.run')
def test_remote_executor_checks_returncode(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 123

    steps = [
        BuildStep(command='cwd test command'),
    ]

    executor = RemoteExecutor('remote_host')

    with pytest.raises(ProcessError) as excinfo:
        executor.run_multiple(steps)

    assert excinfo.value.return_code == 123


@patch('cook.executors.ProcessRunner')
def test_local_executor_returncodes(MockProcessRunner):
    mock_process_runner = MockProcessRunner.return_value
    mock_process_runner.run.return_value.returncode = 123

    steps = [
        BuildStep(command='cwd test command', check=False),
        BuildStep(workdir='work', command='test command', expected_return_code=123),
    ]

    executor = LocalExecutor()
    executor.run_multiple(steps)

    expected_calls = (
        call(
            'cwd test command',
            workdir='.',
        ),
        call(
            'test command',
            workdir='work',
        ),
    )

    assert mock_process_runner.run.call_count == 2
    mock_process_runner.run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_remote_executor_returncodes(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 123

    steps = [
        BuildStep(command='cwd test command', check=False),
        BuildStep(workdir='work', command='test command', expected_return_code=123),
    ]

    executor = RemoteExecutor('remote_host')
    executor.run_multiple(steps)

    expected_calls = (
        call(
            "ssh remote_host 'cd . && cwd test command'",
            shell=True,
        ),
        call(
            "ssh remote_host 'cd work && test command'",
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_has_calls(expected_calls)
