import pytest

from cook.sync import SyncDirectory, SyncExclude, SyncFile

HOSTNAME = 'argon'
LOCAL_PATH_BASE = 'cook/local'
REMOTE_PATH_BASE = 'cook/remote'


def test_sync_attributes():
    assert SyncFile('test/sync/file').is_exclude == False
    assert SyncDirectory('test/sync/dir').is_exclude == False
    assert SyncExclude('test/sync/exclude').is_exclude == True


def test_sync_file_send():
    sync_file = SyncFile('test/sync/file')
    src, dst = sync_file.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    assert src == f'{LOCAL_PATH_BASE}/test/sync/file'
    assert dst == f'{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/file'


def test_sync_file_receive():
    sync_file = SyncFile('test/sync/file')
    src, dst = sync_file.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    assert src == f'{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/file'
    assert dst == f'{LOCAL_PATH_BASE}/test/sync/file'


def test_sync_directory_send():
    sync_directory = SyncDirectory('test/sync/dir')
    src, dst = sync_directory.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    # dir source must end with /
    assert src == f'{LOCAL_PATH_BASE}/test/sync/dir/'
    assert dst == f'{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/dir'


def test_sync_directory_receive():
    sync_directory = SyncDirectory('test/sync/dir')
    src, dst = sync_directory.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    # dir source must end with /
    assert src == f'{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/dir/'
    assert dst == f'{LOCAL_PATH_BASE}/test/sync/dir'


def test_sync_file_send_absolute():
    sync_file = SyncFile('/test/sync/file')
    src, dst = sync_file.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    assert src == '/test/sync/file'
    assert dst == f'{HOSTNAME}:/test/sync/file'


def test_sync_file_receive():
    sync_file = SyncFile('/test/sync/file')
    src, dst = sync_file.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    assert src == f'{HOSTNAME}:/test/sync/file'
    assert dst == '/test/sync/file'


def test_sync_directory_send():
    sync_directory = SyncDirectory('/test/sync/dir')
    src, dst = sync_directory.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    # dir source must end with /
    assert src == '/test/sync/dir/'
    assert dst == f'{HOSTNAME}:/test/sync/dir'


def test_sync_directory_receive():
    sync_directory = SyncDirectory('/test/sync/dir')
    src, dst = sync_directory.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    # dir source must end with /
    assert src == f'{HOSTNAME}:/test/sync/dir/'
    assert dst == '/test/sync/dir'
