# type: ignore

from cook.sync import SyncDirectory, SyncFile

HOSTNAME = "argon"
LOCAL_PATH_BASE = "cook/local"
REMOTE_PATH_BASE = "cook/remote"


def test_sync_file_send() -> None:
    sync_file = SyncFile("test/sync/file")
    src, dst = sync_file.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    assert src == f"{LOCAL_PATH_BASE}/test/sync/file"
    assert dst == f"{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/file"


def test_sync_file_receive() -> None:
    sync_file = SyncFile("test/sync/file")
    src, dst = sync_file.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    assert src == f"{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/file"
    assert dst == f"{LOCAL_PATH_BASE}/test/sync/file"


def test_sync_directory_send() -> None:
    sync_directory = SyncDirectory("test/sync/dir")
    src, dst = sync_directory.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    # dir source must end with /
    assert src == f"{LOCAL_PATH_BASE}/test/sync/dir/"
    assert dst == f"{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/dir"


def test_sync_directory_receive() -> None:
    sync_directory = SyncDirectory("test/sync/dir")
    src, dst = sync_directory.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    # dir source must end with /
    assert src == f"{HOSTNAME}:{REMOTE_PATH_BASE}/test/sync/dir/"
    assert dst == f"{LOCAL_PATH_BASE}/test/sync/dir"


def test_sync_file_send_absolute() -> None:
    sync_file = SyncFile("/test/sync/file")
    src, dst = sync_file.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    assert src == "/test/sync/file"
    assert dst == f"{HOSTNAME}:/test/sync/file"


def test_sync_file_receive() -> None:
    sync_file = SyncFile("/test/sync/file")
    src, dst = sync_file.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    assert src == f"{HOSTNAME}:/test/sync/file"
    assert dst == "/test/sync/file"


def test_sync_directory_send() -> None:
    sync_directory = SyncDirectory("/test/sync/dir")
    src, dst = sync_directory.parse(
        src_path=LOCAL_PATH_BASE,
        dst_hostname=HOSTNAME,
        dst_path=REMOTE_PATH_BASE,
    )
    # dir source must end with /
    assert src == "/test/sync/dir/"
    assert dst == f"{HOSTNAME}:/test/sync/dir"


def test_sync_directory_receive() -> None:
    sync_directory = SyncDirectory("/test/sync/dir")
    src, dst = sync_directory.parse(
        src_hostname=HOSTNAME,
        src_path=REMOTE_PATH_BASE,
        dst_path=LOCAL_PATH_BASE,
    )
    # dir source must end with /
    assert src == f"{HOSTNAME}:/test/sync/dir/"
    assert dst == "/test/sync/dir"
