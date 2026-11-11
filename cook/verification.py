from .configuration import ProjectConfiguration
from .project import Project


class Verification:
    def __init__(self, configuration: ProjectConfiguration) -> None:
        self.configuration = configuration
        self._projects = {p.name: p for p in configuration.projects}

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        for project in self.configuration.projects:
            if project.components is not None:
                warnings.extend(f"Project {project.name}: {p}" for p in self._component_problems(project))
                continue

            # TODO
            # project_problems, servers = self._leaf_checks(project)
            # warnings.extend(f"Project {project.name}: {p}" for p in project_problems)
            # for server, problems in servers.items():
            #     warnings.extend(f"Project {project.name}, build server {server}: {p}" for p in problems)
        return warnings

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
