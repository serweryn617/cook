from build import BuildStep, BuildServer, LocalBuildServer
from sync import SyncItem

class Project:
    def __init__(
            self,
            *,
            steps: list[BuildStep],
            servers: list[BuildServer] = [LocalBuildServer()],
            send: list[SyncItem] = [],
            receive: list[SyncItem] = [],
        ):
        self.steps = steps
        self.servers = servers
        self.send = send
        self.receive = receive
