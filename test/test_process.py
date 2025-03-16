from unittest.mock import MagicMock, call, patch

import pytest

from cook.exception import ConfigurationError
from cook.process import ProcessRunner, SSHProcessRunner


@patch('os.name', 'posix')
@patch('shutil.which')
@patch('subprocess.run')
def test_process_runner_default_executable(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value.returncode = 123
    mock_shutil_which.return_value = '/bin/shell'

    runner = ProcessRunner()
    result = runner.run('cwd test command')

    mock_shutil_which.assert_called_once_with(ProcessRunner.POSIX_EXECUTABLE)
    mock_subprocess_run.assert_called_once_with('cwd test command', cwd=None, shell=True, executable='/bin/shell')
    assert result.returncode == 123


@patch('os.name', 'nt')
@patch('shutil.which')
@patch('subprocess.run')
def test_process_runner_default_executable_nt(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value.returncode = 321
    mock_shutil_which.return_value = 'C/bin/powershell'

    runner = ProcessRunner()
    result = runner.run('cwd test command', 'workdir')

    mock_shutil_which.assert_called_once_with(ProcessRunner.NT_EXECUTABLE)
    mock_subprocess_run.assert_called_once_with('cwd test command', cwd='workdir', shell=True, executable='C/bin/powershell')
    assert result.returncode == 321


@patch('shutil.which')
@patch('subprocess.run')
def test_process_runner_custom_executable(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value.returncode = 0
    mock_shutil_which.return_value = '/bin/custom_shell'

    runner = ProcessRunner('custom_shell')
    result = runner.run('cwd test command')

    mock_shutil_which.assert_called_once_with('custom_shell')
    mock_subprocess_run.assert_called_once_with('cwd test command', cwd=None, shell=True, executable='/bin/custom_shell')
    assert result.returncode == 0


@patch('shutil.which')
@patch('subprocess.run')
def test_process_runner_custom_executable_not_found(mock_subprocess_run, mock_shutil_which):
    mock_subprocess_run.return_value.returncode = 1
    mock_shutil_which.return_value = None

    with pytest.raises(ConfigurationError) as excinfo:
        ProcessRunner('custom_shell')

    mock_shutil_which.assert_called_once_with('custom_shell')
