# type: ignore

from pathlib import Path

import pytest

from cook.build_server import BuildServer, LocalBuildServer, RemoteBuildServer
from cook.build_step import BuildStep
from cook.configuration import ProjectConfiguration
from cook.exception import ConfigurationError
from cook.server_checker import NOT_DEFINED, ServerChecker
from cook.sync import SyncFile


class MockRecipe:
    def __init__(self, projects, base_path, executable=None) -> None:
        self.default_project = None
        self.default_build_server = None
        self.executable = executable
        self.projects = projects
        self.base_path = Path(base_path)


@pytest.fixture
def tools(monkeypatch):
    """Pretend ssh and rsync are installed."""
    monkeypatch.setattr("cook.server_checker.shutil.which", lambda name: f"/usr/bin/{name}")


def check(projects, base_path, project, executable=None):
    configuration = ProjectConfiguration(MockRecipe(projects, base_path, executable))
    return ServerChecker(configuration).check(project)


def steps():
    return [BuildStep(command="true")]


def test_all_servers_are_listed(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "b": {"build_steps": steps(), "build_servers": [RemoteBuildServer("remote")]},
    }
    result = check(projects, tmp_path, "a")

    assert list(result) == ["local", "remote"]
    assert result["local"] == []
    assert result["remote"] == [NOT_DEFINED]


def test_incomplete_definitions(tools, tmp_path) -> None:
    projects = {
        "a": {
            "build_steps": steps(),
            "build_servers": [
                LocalBuildServer(),
                BuildServer("no_path"),
                RemoteBuildServer("empty_address", address=" "),
                RemoteBuildServer("dup"),
                RemoteBuildServer("dup"),
            ],
        },
    }
    result = check(projects, tmp_path, "a")

    assert result["local"] == []
    assert result["no_path"] == ["no build path defined"]
    assert result["empty_address"] == ["empty address"]
    assert result["dup"] == ["defined more than once"]


def test_local_build_path_must_exist(tools, tmp_path) -> None:
    projects = {
        "a": {
            "build_steps": steps(),
            "build_servers": [BuildServer("ok", build_path=".", is_local=True), BuildServer("bad", build_path="missing", is_local=True)],
        },
    }
    result = check(projects, tmp_path, "a")

    assert result["ok"] == []
    assert "does not exist" in result["bad"][0]


def test_missing_executable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("cook.server_checker.shutil.which", lambda name: None)
    projects = {"a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]}}

    assert check(projects, tmp_path, "a", executable="zsh") == {"local": ["executable not found: zsh"]}
    assert check(projects, tmp_path, "a") == {"local": []}


def test_missing_remote_tools(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("cook.server_checker.shutil.which", lambda name: "/usr/bin/ssh" if name == "ssh" else None)
    monkeypatch.setattr("cook.server_checker.platform.system", lambda: "Linux")
    projects = {
        "no_files": {"build_steps": steps(), "build_servers": [RemoteBuildServer("remote")]},
        "files": {"build_steps": steps(), "send": [SyncFile("a")], "build_servers": [RemoteBuildServer("remote")]},
    }

    assert check(projects, tmp_path, "no_files") == {"remote": []}
    assert check(projects, tmp_path, "files") == {"remote": ["rsync not found"]}


def test_skipped_server_needs_no_tools(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("cook.server_checker.shutil.which", lambda name: None)
    projects = {"a": {"build_steps": steps(), "build_servers": [RemoteBuildServer("remote", skip=True)]}}

    assert check(projects, tmp_path, "a") == {"remote": []}


def test_override_applies_to_every_server(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer(override=True), RemoteBuildServer("remote")]},
        "b": {"build_steps": steps(), "build_servers": [RemoteBuildServer("other")]},
    }
    result = check(projects, tmp_path, "a")

    assert result == {"local": [], "other": [], "remote": []}


def test_multiple_overrides(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer(override=True), RemoteBuildServer("remote", override=True)]},
    }
    result = check(projects, tmp_path, "a")

    assert result["local"] == ["multiple server overrides defined"]
    assert result["remote"] == ["multiple server overrides defined"]


def test_composite_needs_every_component(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer(), RemoteBuildServer("remote")]},
        "b": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "all": {"components": ["a", "b"]},
    }
    result = check(projects, tmp_path, "all")

    assert result["local"] == []
    assert result["remote"] == [f"b: {NOT_DEFINED}"]


def test_composite_cycle(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "x": {"components": ["y"]},
        "y": {"components": ["x"]},
    }
    result = check(projects, tmp_path, "x")

    assert len(result["local"]) == 1
    assert result["local"][0].endswith("circular component reference: x -> y -> x")


def test_setup_rejects_circular_components(tmp_path) -> None:
    projects = {
        "x": {"components": ["y"]},
        "y": {"components": ["z"]},
        "z": {"components": ["x"]},
        "self": {"components": ["self"]},
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
    }
    configuration = ProjectConfiguration(MockRecipe(projects, tmp_path))

    with pytest.raises(ConfigurationError, match="Circular component reference: x -> y -> z -> x"):
        configuration.setup("x", "local")
    with pytest.raises(ConfigurationError, match="Circular component reference: self -> self"):
        configuration.setup("self", "local")


def test_setup_rejects_unknown_component(tmp_path) -> None:
    projects = {
        "x": {"components": ["nope"]},
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
    }
    configuration = ProjectConfiguration(MockRecipe(projects, tmp_path))

    with pytest.raises(ConfigurationError, match="Unknown component nope in project x"):
        configuration.setup("x", "local")


def make_checker(projects, base_path, executable=None):
    return ServerChecker(ProjectConfiguration(MockRecipe(projects, base_path, executable)))


def test_unusable_projects(tools, tmp_path) -> None:
    projects = {
        "good": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "bad": {"build_steps": steps(), "build_servers": [BuildServer("broken")]},
        "both": {"components": ["good", "bad"]},
        "only_good": {"components": ["good"]},
    }
    unusable = make_checker(projects, tmp_path).check_projects()

    assert list(unusable) == ["bad", "both"]


def test_warnings_for_every_problem(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer(), BuildServer("broken"), RemoteBuildServer("remote", address=" ")]},
        "multi": {"build_steps": steps(), "build_servers": [LocalBuildServer(override=True), RemoteBuildServer("remote", override=True)]},
    }
    warnings = make_checker(projects, tmp_path).warnings()

    assert warnings == [
        "Project a, build server broken: no build path defined",
        "Project a, build server remote: empty address",
        "Project multi: multiple server overrides defined",
    ]


def test_no_warnings_for_valid_recipe(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "b": {"build_steps": steps(), "build_servers": [RemoteBuildServer("remote")]},
        "all": {"components": ["a", "b"]},
    }

    assert make_checker(projects, tmp_path).warnings() == []


def test_component_warnings(tools, tmp_path) -> None:
    projects = {
        "a": {"build_steps": steps(), "build_servers": [LocalBuildServer()]},
        "x": {"components": ["y", "nope"]},
        "y": {"components": ["x"]},
        "z": {"components": ["x"]},
    }
    warnings = make_checker(projects, tmp_path).warnings()

    assert warnings == [
        "Project x: unknown component nope",
        "Project x: circular component reference: x -> y -> x",
        "Project y: circular component reference: y -> x -> y",
    ]
