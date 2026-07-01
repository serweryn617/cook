class BuildServer:
    def __init__(
        self,
        name: str,
        *,
        address: str | None = None,
        build_path: str | None = None,
        skip: bool = False,
        override: bool = False,
        is_local: bool = False,
    ) -> None:
        self.name = name
        # TODO: Add the ability to sync files locally
        self.address = address or name
        self.build_path = build_path
        self.skip = skip
        self.override = override
        self.is_local = is_local


class LocalBuildServer(BuildServer):
    def __init__(self, *, skip: bool = False, override: bool = False) -> None:
        super().__init__(name="local", build_path=".", skip=skip, override=override, is_local=True)


class RemoteBuildServer(BuildServer):
    def __init__(
        self,
        name: str,
        *,
        build_path: str = "~",
        address: str | None = None,
        skip: bool = False,
        override: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            address=address,
            build_path=build_path,
            skip=skip,
            override=override,
            is_local=False,
        )
