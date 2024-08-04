from pathlib import Path


class RsyncItem:
    is_exclude = False

    def __init__(self, path: str):
        self.path = path


class SyncFile(RsyncItem):
    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> (str, str):
        # TODO: how to handle absolute paths?
        # different base path on remote server not supported at the moment for absolute paths
        src = Path(src_path) / self.path
        src = src.as_posix()
        if src_hostname:
            src = src_hostname + ':' + src

        dst = Path(dst_path) / self.path
        dst = dst.as_posix()
        if dst_hostname:
            dst = dst_hostname + ':' + dst

        return src, dst


class SyncDirectory(SyncFile):
    def __init__(self, path: str = ''):
        self.path = path

    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> (str, str):
        src, dst = super().parse(src_hostname, src_path, dst_hostname, dst_path)

        # Add slash at the end to treat source as directory
        return src + '/', dst


class SyncExclude(RsyncItem):
    is_exclude = True

    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> str:
        return self.path
