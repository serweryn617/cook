from collections.abc import Sequence
from copy import copy
from enum import Enum, auto
from pathlib import Path

from .build_server import BuildServer
from .build_step import BuildStep
from .exception import ConfigurationError
from .project import Project, convert_projects
from .recipe import Recipe
from .sync import SyncItem


class BuildType(Enum):
    LOCAL = auto()
    REMOTE = auto()
    COMPOSITE = auto()


class ProjectConfiguration:
    def __init__(self, recipe: Recipe) -> None:
        self.projects = convert_projects(recipe.projects)
        self.build_servers = self._preprocess_build_servers()

        self.default_project = recipe.default_project
        self.default_build_server = recipe.default_build_server
        self.executable = recipe.executable

        self.base_path = recipe.base_path
        self.skip = False

    def setup(self, project: str | None = None, server: str | None = None) -> None:
        if project is None:
            project = self.default_project
        if project is None:
            raise ConfigurationError("No project selected!")

        if server is None:
            server = self.default_build_server
        if server is None:
            raise ConfigurationError("No build server selected!")

        self._set_project(project)
        self._set_build_server(server)

        if not self._is_composite():
            self._update_paths()

        # TODO: validate recipe contents and print warnings

    def _preprocess_build_servers(self) -> list[str]:
        build_servers: set[str] = set()
        for project in self.projects:
            if project.components is not None:
                continue
            if not project.build_servers:
                raise ConfigurationError(f"Build servers list not defined for project {project.name}")
            build_servers.update([b.name for b in project.build_servers])

        build_servers_list = sorted(build_servers)
        if "local" in build_servers_list:
            build_servers_list.remove("local")
            build_servers_list.insert(0, "local")

        return build_servers_list

    def _set_project(self, project_name: str) -> None:
        projects_by_name = {p.name: p for p in self.projects}
        project_defined = project_name in projects_by_name

        if not project_defined:
            # TODO: Print: did you mean xyz?
            raise ConfigurationError(f"No such project {project_name}")

        self.project = projects_by_name[project_name]

    def _set_build_server(self, build_server_name: str) -> None:
        assert isinstance(self.project, Project)

        server_override = self._get_build_server_override()
        if server_override is not None:
            build_server_name = server_override

        if self._is_composite():
            self.build_server = BuildServer(name=build_server_name)
            return

        for build_server in self.project.build_servers:
            if build_server.name == build_server_name:
                self.build_server = build_server
                break
        else:
            raise ConfigurationError(f"Build server {build_server_name} not defined for {self.project}")

        if self.build_server.skip:
            self.skip = True

    def _get_build_server_override(self) -> str | None:
        build_servers = self.project.build_servers

        overrides: list[str] = []
        for build_server in build_servers:
            if build_server.override:
                overrides.append(build_server.name)

        if len(overrides) > 1:
            raise ConfigurationError(f"Multiple server overrides defined for {self.project}")

        if overrides:
            return overrides[0]

    def _update_paths(self) -> None:
        if self.build_server.build_path is None:
            raise ConfigurationError(f"No build path defined for {self.project} on build server {self.build_server.name}")

        build_path = Path(self.build_server.build_path)
        if self._is_local() and not build_path.is_absolute():
            self.build_path = (self.base_path / build_path).resolve()
        else:
            self.build_path = build_path

    def _is_composite(self) -> bool:
        is_composite = self.project.components is not None
        return is_composite

    def _is_local(self) -> bool:
        return self.build_server.is_local

    def get_build_type(self) -> BuildType:
        if self._is_composite():
            build_type = BuildType.COMPOSITE
        elif self._is_local():
            build_type = BuildType.LOCAL
        else:
            build_type = BuildType.REMOTE

        return build_type

    def get_build_server(self) -> str:
        if self.build_server.address is not None:
            return self.build_server.address
        return self.build_server.name

    def get_base_paths(self) -> tuple[str, str]:
        return self.base_path.as_posix(), self.build_path.as_posix()

    def get_files_to_send(self) -> Sequence[SyncItem] | None:
        if self.skip:
            return None

        return self.project.send

    def get_files_to_receive(self) -> Sequence[SyncItem] | None:
        if self.skip:
            return None

        return self.project.receive

    def get_build_steps(self) -> list[BuildStep] | None:
        if self.skip:
            return None

        build_steps = self.project.build_steps

        if build_steps is None:
            return None

        parsed_build_steps: list[BuildStep] = []

        for step in build_steps:
            # shallow copy is enough as only a str is modified but be careful
            parsed_step = copy(step)
            parsed_step.workdir = self.build_path / parsed_step.workdir
            parsed_build_steps.append(parsed_step)

        return parsed_build_steps

    def get_components(self) -> Sequence[str] | None:
        return self.project.components

    def get_executable(self) -> str | None:
        return self.executable

    def get_project_names(self) -> list[str]:
        project_names = [p.name for p in self.projects]
        return project_names
