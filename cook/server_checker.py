import platform
import shutil
from pathlib import Path

from .build_server import BuildServer
from .configuration import ProjectConfiguration
from .project import Project

NOT_DEFINED = "not defined for this project"
NO_USABLE_SERVER = "no usable build servers"

type Problems = dict[str, list[str]]


class ServerChecker:
    """Finds which build servers of a project are correctly defined and will work.

    Only cheap, local checks are done (no network access). A server has problems when:
      * its definition is incomplete (empty name/address, missing build path, ...),
      * the same name is defined twice or several overrides are defined,
      * a local build path does not exist or the configured executable is missing,
      * the required tools (ssh, rsync/scp) are not installed,
      * any component of a composite project cannot use it.
    """

    def __init__(self, configuration: ProjectConfiguration) -> None:
        self.configuration = configuration
        self._projects = {p.name: p for p in configuration.projects}

    # --- public API ----------------------------------------------------------------------------

    def check(self, project_name: str) -> Problems:
        """Map every known build server name to the problems that prevent using it for a project.

        A server with an empty problem list is usable. The result is ordered like `configuration.build_servers`.
        """
        return self._evaluate(project_name, ())

    def check_projects(self) -> dict[str, str]:
        """Map every project that has no usable build server to a short note."""
        unusable: dict[str, str] = {}
        for project in self.configuration.projects:
            if all(problems for problems in self.check(project.name).values()):
                unusable[project.name] = NO_USABLE_SERVER
        return unusable

    def warnings(self) -> list[str]:
        """One message for every problem found in the definitions of all projects."""
        warnings: list[str] = []
        for project in self.configuration.projects:
            if project.components is not None:
                warnings.extend(f"Project {project.name}: {p}" for p in self._component_problems(project))
                continue

            project_problems, servers = self._leaf_checks(project)
            warnings.extend(f"Project {project.name}: {p}" for p in project_problems)
            for server, problems in servers.items():
                warnings.extend(f"Project {project.name}, build server {server}: {p}" for p in problems)
        return warnings

    # --- project level -------------------------------------------------------------------------

    def _all(self, *problems: str) -> Problems:
        return {name: list(problems) for name in self.configuration.build_servers}

    def _evaluate(self, project_name: str, stack: tuple[str, ...]) -> Problems:
        project = self._projects.get(project_name)
        if project is None:
            return self._all(f"unknown project {project_name}")

        if project.components is not None:
            return self._evaluate_composite(project, stack)
        return self._evaluate_leaf(project)

    def _evaluate_composite(self, project: Project, stack: tuple[str, ...]) -> Problems:
        stack = (*stack, project.name)
        results: Problems = {name: [] for name in self.configuration.build_servers}

        for component in project.components or ():
            if component in stack:
                return self._all(f"circular component reference: {' -> '.join((*stack, component))}")

            component_results = self._evaluate(component, stack)
            for name, problems in component_results.items():
                results[name].extend(f"{component}: {p}" for p in problems)

        return results

    def _evaluate_leaf(self, project: Project) -> Problems:
        project_problems, checked = self._leaf_checks(project)
        if project_problems:
            return self._all(*project_problems)

        overrides = [s for s in project.build_servers if s.override]
        if overrides:
            # whatever server is requested, the override is the one that gets used
            override_problems = checked[overrides[0].name]
            return {name: list(override_problems) for name in self.configuration.build_servers}

        return {name: list(checked.get(name, [NOT_DEFINED])) for name in self.configuration.build_servers}

    def _leaf_checks(self, project: Project) -> tuple[list[str], dict[str, list[str]]]:
        """Return (problems of the project itself, problems of each server defined in it)."""
        servers = list(project.build_servers)
        if not servers:
            return ["no build servers defined"], {}

        if sum(s.override for s in servers) > 1:
            return ["multiple server overrides defined"], {}

        names = [s.name for s in servers]
        checked: dict[str, list[str]] = {}
        for server in servers:
            if server.name in checked:
                continue  # the configuration always picks the first definition
            problems = self._check_server(project, server)
            if names.count(server.name) > 1:
                problems.append("defined more than once")
            checked[server.name] = problems

        return [], checked

    def _component_problems(self, project: Project) -> list[str]:
        problems = [f"unknown component {c}" for c in project.components or () if c not in self._projects]

        cycle = self._find_cycle(project.name)
        if cycle is not None:
            problems.append(f"circular component reference: {' -> '.join(cycle)}")
        return problems

    def _find_cycle(self, start: str) -> tuple[str, ...] | None:
        """Return a chain of components leading from a project back to itself, if there is one."""

        def walk(name: str, path: tuple[str, ...]) -> tuple[str, ...] | None:
            project = self._projects.get(name)
            if project is None or project.components is None:
                return None

            for component in project.components:
                if component == start:
                    return (*path, component)
                if component in path:
                    continue  # a cycle that does not include the start project
                found = walk(component, (*path, component))
                if found is not None:
                    return found
            return None

        return walk(start, (start,))

    # --- single server -------------------------------------------------------------------------

    def _check_server(self, project: Project, server: BuildServer) -> list[str]:
        problems = self._check_definition(server)
        if problems or server.skip:
            return problems  # a skipped server runs nothing, so it needs nothing to be installed

        if server.is_local:
            problems.extend(self._check_local(server))
        else:
            problems.extend(self._check_remote(project))
        return problems

    @staticmethod
    def _check_definition(server: BuildServer) -> list[str]:
        problems: list[str] = []
        if not isinstance(server.name, str) or not server.name.strip():
            problems.append("empty name")
        if server.address is not None and not server.address.strip():
            problems.append("empty address")
        if server.build_path is None or not str(server.build_path).strip():
            problems.append("no build path defined")
        return problems

    def _check_local(self, server: BuildServer) -> list[str]:
        problems: list[str] = []

        build_path = Path(str(server.build_path))
        if not build_path.is_absolute():
            build_path = self.configuration.base_path / build_path
        if not build_path.is_dir():
            problems.append(f"build path {build_path} does not exist")

        executable = self.configuration.get_executable()
        if executable is not None and shutil.which(executable) is None:
            problems.append(f"executable not found: {executable}")

        return problems

    @staticmethod
    def _check_remote(project: Project) -> list[str]:
        problems: list[str] = []

        if shutil.which("ssh") is None:
            problems.append("ssh not found")

        if project.send or project.receive:
            tool = "scp" if platform.system() == "Windows" else "rsync"
            if shutil.which(tool) is None:
                problems.append(f"{tool} not found")

        return problems
