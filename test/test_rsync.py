from unittest.mock import MagicMock, call, patch

import pytest

from cook.exception import ProcessError
from cook.rsync import Rsync
from cook.sync import SyncDirectory, SyncExclude, SyncFile

RSYNC_COMMAND = 'rsync --compress --delete --links --recursive --mkpath --times --info=progress2 {infile} {outfile}'


@patch('subprocess.run')
def test_rsync_send(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    file_list = [
        SyncFile('path/to/file.txt'),
        SyncDirectory('path/to/dir'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir')
    rsync.send(file_list)

    expected_calls = (
        call(
            RSYNC_COMMAND.format(
                infile='local/dir/path/to/file.txt',
                outfile='server:remote/dir/path/to/file.txt',
            ),
            shell=True,
        ),
        call(
            RSYNC_COMMAND.format(
                infile='local/dir/path/to/dir/',  # trailing slash
                outfile='server:remote/dir/path/to/dir',
            ),
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_rsync_send_exclude(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    file_list = [
        SyncFile('path/to/file.txt'),
        SyncDirectory('path/to/dir'),
        SyncExclude('path/to/excluded.txt'),
        SyncExclude('path/to/ignored.txt'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir')
    rsync.send(file_list)

    expected_calls = (
        call(
            RSYNC_COMMAND.format(
                infile='local/dir/path/to/file.txt',
                outfile='server:remote/dir/path/to/file.txt',
            )
            + ' --exclude=path/to/excluded.txt --exclude=path/to/ignored.txt',
            shell=True,
        ),
        call(
            RSYNC_COMMAND.format(
                infile='local/dir/path/to/dir/',  # trailing slash
                outfile='server:remote/dir/path/to/dir',
            )
            + ' --exclude=path/to/excluded.txt --exclude=path/to/ignored.txt',
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_rsync_receive(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    file_list = [
        SyncFile('path/to/file.txt'),
        SyncDirectory('path/to/dir'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir')
    rsync.receive(file_list)

    expected_calls = (
        call(
            RSYNC_COMMAND.format(
                infile='server:remote/dir/path/to/file.txt',
                outfile='local/dir/path/to/file.txt',
            ),
            shell=True,
        ),
        call(
            RSYNC_COMMAND.format(
                infile='server:remote/dir/path/to/dir/',  # trailing slash
                outfile='local/dir/path/to/dir',
            ),
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_rsync_receive_exclude(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    file_list = [
        SyncFile('path/to/file.txt'),
        SyncDirectory('path/to/dir'),
        SyncExclude('path/to/excluded.txt'),
        SyncExclude('path/to/ignored.txt'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir')
    rsync.receive(file_list)

    expected_calls = (
        call(
            RSYNC_COMMAND.format(
                infile='server:remote/dir/path/to/file.txt',
                outfile='local/dir/path/to/file.txt',
            )
            + ' --exclude=path/to/excluded.txt --exclude=path/to/ignored.txt',
            shell=True,
        ),
        call(
            RSYNC_COMMAND.format(
                infile='server:remote/dir/path/to/dir/',  # trailing slash
                outfile='local/dir/path/to/dir',
            )
            + ' --exclude=path/to/excluded.txt --exclude=path/to/ignored.txt',
            shell=True,
        ),
    )

    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch('subprocess.run')
def test_rsync_dry_run(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0

    file_list = [
        SyncFile('path/to/file.txt'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir', dry_run=True)

    rsync.send(file_list)
    rsync.receive(file_list)

    assert not mock_subprocess_run.called


@patch('subprocess.run')
def test_rsync_checks_returncode(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 5

    file_list = [
        SyncFile('path/to/file.txt'),
    ]

    rsync = Rsync('server', 'local/dir', 'remote/dir')

    with pytest.raises(ProcessError) as excinfo:
        rsync.send(file_list)

    assert excinfo.value.return_code == 5
