# type: ignore

import pytest

from cook.library.selector import DisabledSelection, SelectionInterrupt, Selector
from cook.library.terminal import UnixKeys

DOWN = UnixKeys.down
UP = UnixKeys.up


def select(monkeypatch, keys, elements=("a", "b", "c", "d"), **kwargs):
    pressed = iter(keys)
    monkeypatch.setattr("cook.library.selector.getkey", lambda: next(pressed))
    return Selector(elements, "item", **kwargs).select()


def test_plain_selection(monkeypatch) -> None:
    assert select(monkeypatch, [DOWN, "\r"]) == "b"
    assert select(monkeypatch, [UP, "\r"]) == "d"  # wraps around


def test_cursor_can_move_onto_disabled_elements(monkeypatch) -> None:
    disabled = {"b": "no reason"}

    with pytest.raises(DisabledSelection) as error:
        select(monkeypatch, [DOWN, "\r"], disabled=disabled)

    assert error.value.element == "b"
    assert error.value.note == "no reason"


def test_enabled_elements_still_selectable(monkeypatch) -> None:
    disabled = {"b": "no", "c": "no"}

    assert select(monkeypatch, [DOWN, DOWN, DOWN, "\r"], disabled=disabled) == "d"
    assert select(monkeypatch, ["\r"], disabled=disabled) == "a"


def test_disabled_default_falls_back_to_first_enabled(monkeypatch) -> None:
    assert select(monkeypatch, ["\r"], default="a", disabled={"a": "no"}) == "b"
    assert select(monkeypatch, ["\r"], default="c", disabled={"a": "no"}) == "c"


def test_all_disabled_exits_on_enter(monkeypatch) -> None:
    with pytest.raises(DisabledSelection):
        select(monkeypatch, ["\r"], elements=("a", "b"), disabled={"a": "x", "b": "y"})


def test_disabled_selection_is_an_interrupt(monkeypatch) -> None:
    assert issubclass(DisabledSelection, SelectionInterrupt)


def test_disabled_elements_are_dimmed(monkeypatch, capsys) -> None:
    select(monkeypatch, ["\r"], disabled={"b": "not defined"})
    out = capsys.readouterr().out

    assert "b (not defined)" in out
    assert "\x1b[2m" in out


def test_cancel(monkeypatch) -> None:
    with pytest.raises(SelectionInterrupt):
        select(monkeypatch, ["q"])
