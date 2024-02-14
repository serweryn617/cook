import subprocess


class Rsync:
    command = [
        'rsync',
        '--compress',
        '--delete',
        '--links',
        '--recursive',
        '--times',
        '--info=progress2',
    ]

    def __init__(self, local_path, hostname, remote_path):
        self.hostname = hostname
        self.local_path = local_path
        self.remote_path = remote_path

    def send(self, files=['*'], exclude=None):
        cmd = Rsync.command + files
        cmd.append(self.hostname + ':' + self.remote_path)

        # TODO: add exclude
        subprocess.check_output(cmd)

    def receive(self, files):
        files = [self.hostname + ':' + file for file in files]
        location = [self.local_path]

        cmd = Rsync.command + files + location

        subprocess.check_output(cmd)
