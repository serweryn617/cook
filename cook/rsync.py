import subprocess
from pathlib import Path


class Rsync:
    command = (
        'rsync',
        '--compress',
        '--delete',
        '--links',
        '--recursive',
        '--times',
        '--info=progress2',
    )
    exclude = '--exclude='

    def __init__(self, hostname, logger=None):  # TODO: add rsync for local
        self.hostname = hostname
        self.logger = logger

    def send(self, files, exclude=None):
        for src, dst in files:
            src = src.rstrip('/') + '/'
            dst = self.hostname + ':' + dst.rstrip('/')

            if self.logger is not None:
                self.logger.remote(f'Transfering {src} to {dst}')

            cmd = list(Rsync.command)

            # if exclude:
            #     cmd += [Rsync.exclude + pattern for pattern in exclude]

            cmd.append(src)
            cmd.append(dst)

            subprocess.check_output(' '.join(cmd), shell=True)

    def receive(self, files):
        for src, dst in files:
            src = self.hostname + ':' + src.rstrip('/') + '/'
            dst = dst.rstrip('/')

            if self.logger is not None:
                self.logger.remote(f'Transfering {src} to {dst}')

            cmd = list(Rsync.command)
            cmd.append(src)
            cmd.append(dst)

            subprocess.check_output(' '.join(cmd), shell=True)
