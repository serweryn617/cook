import subprocess
from pathlib import Path

from .exception import ProcessError


class RsyncItem:
    def __init__(self, path: str):
        self.path = path


class SyncDirectory(RsyncItem):
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


class Rsync:
    command = (
        'rsync',
        '--compress',
        '--delete',
        '--links',
        '--recursive',
        '--mkpath',
        '--times',
        '--info=progress2',
    )
    exclude = '--exclude='

    # TODO: add rsync for local build
    def __init__(self, hostname, local_base, remote_base, logger=None):
        self.hostname = hostname
        self.logger = logger
        self.local_base = local_base
        self.remote_base = remote_base

    def sync(self, src, dst, exludes):
        if self.logger is not None:
            self.logger.rich(f'Transferring: {src} to {dst}\n')

        cmd = list(Rsync.command)
        cmd.append(src)
        cmd.append(dst)
        cmd.extend([Rsync.exclude + e for e in exludes])

        result = subprocess.run(' '.join(cmd), shell=True)
        if result.returncode != 0:
            raise ProcessError('rsync returned an error!', result.returncode)

    def _get_exclude_list(self, rsync_items):
        excludes = []
        for rsync_item in rsync_items:
            is_exclude = getattr(rsync_item, 'is_exclude', False)
            if is_exclude:
                excludes.append(rsync_item.parse())
        return excludes

    def sync_multiple(self, rsync_items, **parser_args):
        excludes = self._get_exclude_list(rsync_items)

        if self.logger is not None and excludes:
            self.logger.rich('Excluding:\n')
            for exclude in excludes:
                self.logger.rich(f'  {exclude}\n')

        for rsync_item in rsync_items:
            is_exclude = getattr(rsync_item, 'is_exclude', False)
            if is_exclude:
                continue

            src, dst = rsync_item.parse(**parser_args)

            self.sync(src, dst, excludes)

    def send(self, rsync_items):
        self.sync_multiple(rsync_items, src_base=self.local_base, dst_host=self.hostname, dst_base=self.remote_base)

    def receive(self, rsync_items):
        self.sync_multiple(rsync_items, src_host=self.hostname, src_base=self.remote_base, dst_base=self.local_base)
