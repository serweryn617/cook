import shlex
import subprocess
from pathlib import Path

from .exception import ProcessError
from .library.logger import log


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
    def __init__(self, hostname, local_base, remote_base, dry_run=False):
        self.hostname = hostname
        self.local_base = local_base
        self.remote_base = remote_base
        self.dry_run = dry_run

    def _sync(self, src, dst, exludes):
        cmd = list(Rsync.command)
        cmd.append(src)
        cmd.append(dst)
        cmd.extend([Rsync.exclude + e for e in exludes])

        result = subprocess.run(shlex.join(cmd), shell=True)
        if result.returncode != 0:
            raise ProcessError('rsync returned an error!', result.returncode)

    def _get_exclude_list(self, rsync_items):
        excludes = []
        for rsync_item in rsync_items:
            if rsync_item.is_exclude:
                excludes.append(rsync_item.parse())
        return excludes

    def _sync_multiple(self, rsync_items, **parser_args):
        excludes = self._get_exclude_list(rsync_items)

        if excludes:
            log('Excluding:')
            for exclude in excludes:
                log(f'  {exclude}')

        for rsync_item in rsync_items:
            if rsync_item.is_exclude:
                continue

            src, dst = rsync_item.parse(**parser_args)

            log(f'Transferring: {src} to {dst}')

            if self.dry_run:
                continue

            self._sync(src, dst, excludes)

    def send(self, rsync_items):
        self._sync_multiple(rsync_items, src_path=self.local_base, dst_hostname=self.hostname, dst_path=self.remote_base)

    def receive(self, rsync_items):
        self._sync_multiple(rsync_items, src_hostname=self.hostname, src_path=self.remote_base, dst_path=self.local_base)
