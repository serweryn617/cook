from collections.abc import Sequence
from typing import Any

from .build_server import BuildServer, LocalBuildServer
from .build_step import BuildStep, convert_build_steps
from .sync import SyncItem


class Project:
    def __init__(
        self,
        *,
        name: str,
        build_steps: Sequence[BuildStep] | None = None,
        build_servers: Sequence[BuildServer] = (LocalBuildServer(),),
        send: Sequence[SyncItem] | None = None,
        receive: Sequence[SyncItem] | None = None,
        components: Sequence[str] | None = None,
    ) -> None:
        self.name = name
        self.build_steps = build_steps
        self.build_servers = build_servers
        self.send = send
        self.receive = receive
        self.components = components


def convert_projects(projects: dict[str, Any] | Sequence[Project]) -> Sequence[Project]:
    # TODO: Before the convert function is called the type should be Any.
    if isinstance(projects, dict):
        return convert_from_dict(projects)
    elif isinstance(projects, (list, tuple)) and all(isinstance(p, Project) for p in projects):  # type: ignore
        return projects
    else:
        raise RuntimeError("Projects should be a dict or list of Projects")


def local_build_from_list(name: str, steps: Sequence[BuildStep]) -> Project:
    return Project(
        name=name,
        build_servers=[LocalBuildServer()],
        build_steps=convert_build_steps(steps),
    )


type DictProject = dict[str, Any]
type ListProject = Sequence[Any]


def convert_from_dict(projects: dict[str, DictProject | ListProject]) -> list[Project]:
    preprocessed_projects: list[Project] = []

    for name, definition in projects.items():
        if isinstance(definition, dict):
            build_steps = convert_build_steps(definition["build_steps"]) if "build_steps" in definition else None
            servers = definition.get("build_servers", [LocalBuildServer()])
            send = definition.get("send", None)
            receive = definition.get("receive", None)
            components = definition.get("components", None)
            project_object = Project(
                name=name,
                build_steps=build_steps,
                build_servers=servers,
                send=send,
                receive=receive,
                components=components,
            )
        elif isinstance(definition, (list, tuple)):
            project_object = local_build_from_list(name, definition)
        else:
            raise RuntimeError("Unknown project format!")

        preprocessed_projects.append(project_object)

    return preprocessed_projects
