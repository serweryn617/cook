import subprocess


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

    def __init__(self, local_path, hostname, remote_path):
        self.hostname = hostname
        self.local_path = local_path
        self.remote_path = remote_path

    def send(self, files, exclude=None):
        cmd = list(Rsync.command)
        
        if exclude:
            cmd += [Rsync.exclude + pattern for pattern in exclude]

        cmd += files
        cmd.append(self.hostname + ':' + self.remote_path)

        subprocess.check_output(' '.join(cmd), shell=True)

    def receive(self, files):
        files = [self.hostname + ':' + file for file in files]
        location = [self.local_path]

        cmd = list(Rsync.command) + files + location

        subprocess.check_output(cmd)
