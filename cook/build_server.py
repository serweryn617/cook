class BuildServer:
    def __init__(self, name, build_path=None, sync_files=None, skip=False, override=False, is_local=None):
        self.name = name
        self.build_path = build_path
        self.sync_files = sync_files
        self.skip = skip
        self.override = override
        self.is_local = is_local


class LocalBuildServer(BuildServer):
    def __init__(self, skip=False, override=False):
        super().__init__(name='local', build_path='.', sync_files=False, skip=skip, override=override, is_local=True)


class RemoteBuildServer(BuildServer):
    def __init__(self, name, build_path, sync_files=True, skip=False, override=False):
        super().__init__(name=name, build_path=build_path, sync_files=sync_files, skip=skip, override=override, is_local=False)
