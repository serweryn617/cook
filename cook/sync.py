from pathlib import Path


class RsyncItem:
    def __init__(self, path: str):
        self.path = path


class SyncDirectory(RsyncItem):
    def __init__(self, path: str = ''):
        self.path = path

    def parse(self, src_host: str = '', src_base: str = '', dst_host: str = '', dst_base: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_base) / self.path
        # Add slash at the end to treat source as directory
        src = src.as_posix() + '/'
        if src_host:
            src = src_host + ':' + src

        dst = Path(dst_base) / self.path
        dst = dst.as_posix()
        if dst_host:
            dst = dst_host + ':' + dst

        return src, dst


class SyncFile(RsyncItem):
    def parse(self, src_host: str = '', src_base: str = '', dst_host: str = '', dst_base: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_base) / self.path
        src = src.as_posix()
        if src_host:
            src = src_host + ':' + src

        dst = Path(dst_base) / self.path
        dst = dst.as_posix()
        if dst_host:
            dst = dst_host + ':' + dst

        return src, dst


class SyncExclude(RsyncItem):
    is_exclude = True

    def parse(self, src_host: str = '', src_base: str = '', dst_host: str = '', dst_base: str = '') -> str:
        return self.path
