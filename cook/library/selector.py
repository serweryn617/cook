import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass

from .key import getkey
from .logger import ORANGE
from .terminal import EscapeCodes, UnixKeys, WindowsKeys


class SelectionInterrupt(Exception):
    pass


class DisabledSelection(SelectionInterrupt):
    """Raised when Enter is pressed on a disabled element."""

    def __init__(self, element: str, note: str) -> None:
        super().__init__(element, note)
        self.element = element
        self.note = note


@dataclass
class Element:
    name: str
    description: str = ""
    disabled: bool = False
    note: str = ""

    def __str__(self) -> str:
        note = f"({self.note}) " if self.note else ""
        return f"{self.name}  {note}{self.description}"


class Selector:
    def __init__(
        self,
        elements: Sequence[Element],
        message: str = "",
        cursor: str = ">",
        default: str | None = None,
    ) -> None:
        self.elements = elements
        self.num = len(elements)
        self.cursor = cursor
        self.cursor_len = len(cursor)
        self.message = message
        self.width = shutil.get_terminal_size().columns
        assert self.cursor_len > 0, "Cursor must be at least 1 character!"

        self.default_index = elements.index(default) if default is not None else 0

    def select(self) -> str:
        print(EscapeCodes.fg(*ORANGE) + f"Select{' ' + self.message if self.message else ''}:" + EscapeCodes.reset)
        print(EscapeCodes.hide_cursor, end="")

        for elem in self.elements:
            line = " " + (" " * self.cursor_len) + " " + self._render(elem)
            if len(line) > self.width:
                line = line[: max(self.width - 3, 0)] + "..."
            print(line)
        print(EscapeCodes.up(self.num) + EscapeCodes.right(1), end="")

        current = self.default_index
        previous = current

        if current:
            print(EscapeCodes.down(current), end="")
        print(self.cursor + EscapeCodes.left(self.cursor_len), end="")
        sys.stdout.flush()

        while True:
            c = getkey()
            # TODO: Remove kj keys, add search instead
            if c in (UnixKeys.up, WindowsKeys.up, "k"):
                current -= 1
            elif c in (UnixKeys.down, WindowsKeys.down, "j"):
                current += 1
            elif c == "\r":
                if self.elements[current].disabled:
                    self._cleanup(current)
                    raise DisabledSelection(self.elements[current].name, self.elements[current].note)
                break
            else:
                self._cleanup(current)
                raise SelectionInterrupt
            current %= self.num

            if current != previous:
                move = EscapeCodes.down(current - previous) if current > previous else EscapeCodes.up(previous - current)
                previous = current

                print(" " * self.cursor_len + EscapeCodes.left(self.cursor_len), end="")
                print(move, end="")
                print(self.cursor + EscapeCodes.left(self.cursor_len), end="")
                sys.stdout.flush()

        self._cleanup(current)
        return self.elements[current].name

    def _render(self, elem: Element) -> str:
        text = str(elem)

        if not elem.disabled:
            return text

        return EscapeCodes.dim + text + EscapeCodes.reset

    def _cleanup(self, current: int) -> None:
        print(EscapeCodes.up(current + 1) + EscapeCodes.line_begin, end="")
        print(EscapeCodes.clear_after_cursor, end="")
        print(EscapeCodes.show_cursor, end="")
        sys.stdout.flush()
