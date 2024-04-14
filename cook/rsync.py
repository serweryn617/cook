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

    def __init__(self, hostname):  # TODO: add rsync for local
        self.hostname = hostname

    def send(self, files, exclude=None):
        for src, dst in files:
            print('Sending', src, 'to', self.hostname + ':' + dst)

            cmd = list(Rsync.command)

            # if exclude:
            #     cmd += [Rsync.exclude + pattern for pattern in exclude]

            cmd.append(src)
            cmd.append(self.hostname + ':' + dst)

            subprocess.check_output(' '.join(cmd), shell=True)

    def receive(self, files):
        for src, dst in files:
            print('Receiving', self.hostname + ':' + src, 'to', dst)

            cmd = list(Rsync.command)
            cmd.append(self.hostname + ':' + src)
            cmd.append(dst)

            subprocess.check_output(' '.join(cmd), shell=True)
