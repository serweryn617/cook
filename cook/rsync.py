import subprocess
from pathlib import Path

from .exception import ProcessError


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
        self.dry_run = False

    def set_dry_run(self, dry_run: bool):
        self.dry_run = dry_run

    def sync(self, src, dst, exludes):
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
            self.logger.log('Excluding:\n')
            for exclude in excludes:
                self.logger.log(f'  {exclude}\n')

        for rsync_item in rsync_items:
            is_exclude = getattr(rsync_item, 'is_exclude', False)
            if is_exclude:
                continue

            src, dst = rsync_item.parse(**parser_args)

            if self.logger is not None:
                self.logger.log(f'Transferring: {src} to {dst}\n')

            if self.dry_run:
                return

            self.sync(src, dst, excludes)

    def send(self, rsync_items):
        self.sync_multiple(rsync_items, src_base=self.local_base, dst_host=self.hostname, dst_base=self.remote_base)

    def receive(self, rsync_items):
        self.sync_multiple(rsync_items, src_host=self.hostname, src_base=self.remote_base, dst_base=self.local_base)
