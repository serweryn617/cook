from pathlib import Path


class RsyncItem:
    is_exclude = False

    def __init__(self, path: str):
        self.path = path


class SyncDirectory(RsyncItem):
    def __init__(self, path: str = ''):
        self.path = path

    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_path) / self.path
        # Add slash at the end to treat source as directory
        src = src.as_posix() + '/'
        if src_hostname:
            src = src_hostname + ':' + src

        dst = Path(dst_path) / self.path
        dst = dst.as_posix()
        if dst_hostname:
            dst = dst_hostname + ':' + dst

        return src, dst


class SyncFile(RsyncItem):
    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_path) / self.path
        src = src.as_posix()
        if src_hostname:
            src = src_hostname + ':' + src

        dst = Path(dst_path) / self.path
        dst = dst.as_posix()
        if dst_hostname:
            dst = dst_hostname + ':' + dst

        return src, dst


class SyncExclude(RsyncItem):
    is_exclude = True

    def parse(self, src_hostname: str = '', src_path: str = '', dst_hostname: str = '', dst_path: str = '') -> str:
        return self.path
