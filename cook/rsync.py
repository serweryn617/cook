import subprocess
from pathlib import Path


class RsyncDirectory:
    def __init__(self, path: str):
        self.path = path

    def parse(self, src_base: str = '', dst_base: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_base) / self.path
        # Add slash at the end to treat source as directory
        src = src.as_posix() + '/'

        dst = Path(dst_base) / self.path
        dst = dst.as_posix()

        return src, dst


class RsyncFile:
    def __init__(self, path: str):
        self.path = path

    def parse(self, src_base: str = '', dst_base: str = '') -> (str, str):
        # TODO: add support for absolute paths
        src = Path(src_base) / self.path
        src = src.as_posix()

        dst = Path(dst_base) / self.path
        dst = dst.as_posix()

        return src, dst


class Rsync:
    command = (
        'rsync',
        '--compress',
        '--delete',
        '--links',
        '--recursive',
        '--times',
        '--info=progress2',
        '--mkpath',
    )
    exclude = '--exclude='

    def __init__(self, hostname, local_base, remote_base, logger=None):  # TODO: add rsync for local
        self.hostname = hostname
        self.logger = logger
        self.local_base = local_base
        self.remote_base = remote_base

    def send(self, rsync_items, exclude=None):
        for rsync_item in rsync_items:
            src_base = self.local_base
            dst_base = self.hostname + ':' + self.remote_base

            src, dst = rsync_item.parse(src_base=src_base, dst_base=dst_base)

            if self.logger is not None:
                self.logger.remote(f'Transfering {src} to {dst}')

            # TODO: add exclude

            cmd = list(Rsync.command)
            cmd.append(src)
            cmd.append(dst)

            subprocess.check_output(' '.join(cmd), shell=True)

    def receive(self, rsync_items):
        for rsync_item in rsync_items:
            src_base = self.hostname + ':' + self.remote_base
            dst_base = self.local_base

            src, dst = rsync_item.parse(src_base=src_base, dst_base=dst_base)

            if self.logger is not None:
                self.logger.remote(f'Transfering {src} to {dst}')

            # TODO: add exclude

            cmd = list(Rsync.command)
            cmd.append(src)
            cmd.append(dst)

            subprocess.check_output(' '.join(cmd), shell=True)
