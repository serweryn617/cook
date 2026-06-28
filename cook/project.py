from .build_server import BuildServer, LocalBuildServer
from .build_step import BuildStep, convert_build_steps
from .sync import SyncItem


class Project:
    def __init__(
        self,
        *,
        name: str,
        build_steps: list[BuildStep] = None,
        build_servers: list[BuildServer] = (LocalBuildServer(),),
        send: list[SyncItem] = None,
        receive: list[SyncItem] = None,
        components: list[str] = None,
    ):
        self.name = name
        self.build_steps = build_steps
        self.build_servers = build_servers
        self.send = send
        self.receive = receive
        self.components = components


def convert_projects(projects: dict | list[Project]):
    if isinstance(projects, dict):
        return convert_from_dict(projects)
    elif isinstance(projects, list) and all(isinstance(p, Project) for p in projects):
        return projects
    else:
        raise RuntimeError('Projects should be a dict or list of Projects')


def local_build_from_list(name, steps):
    return Project(
        name=name,
        build_servers=[LocalBuildServer()],
        build_steps=convert_build_steps(steps),
    )


def convert_from_dict(projects: dict):
    preprocessed_projects = []

    for name, definition in projects.items():
        if isinstance(definition, dict):
            build_steps = convert_build_steps(definition['build_steps']) if 'build_steps' in definition else None
            servers = definition['build_servers'] if 'build_servers' in definition else [LocalBuildServer()]
            send = definition['send'] if 'send' in definition else None
            receive = definition['receive'] if 'receive' in definition else None
            components = definition['components'] if 'components' in definition else None
            project_object = Project(
                name=name, build_steps=build_steps, build_servers=servers, send=send, receive=receive, components=components
            )
        elif isinstance(definition, (list, tuple)):
            project_object = local_build_from_list(name, definition)
        else:
            raise RuntimeError('Unknown project format!')

        preprocessed_projects.append(project_object)

    return preprocessed_projects
