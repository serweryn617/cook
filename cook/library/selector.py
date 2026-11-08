import shutil
import sys
from collections.abc import Mapping, Sequence

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


class Selector:
    def __init__(
        self,
        elements: Sequence[str],
        message: str = "",
        cursor: str = ">",
        default: str | None = None,
        disabled: Mapping[str, str] | None = None,
    ) -> None:
        """Elements listed in `disabled` are shown dimmed, with the mapped note.

        The cursor can still be moved onto them, but confirming one raises `DisabledSelection`.
        """
        self.elements = elements
        self.disabled = disabled or {}
        self.num = len(elements)
        self.cursor = cursor
        self.cursor_len = len(cursor)
        self.message = message
        assert self.cursor_len > 0, "Cursor must be at least 1 character!"

        self.default_index = elements.index(default) if default is not None else 0
        if elements[self.default_index] in self.disabled:
            # start on something that can be selected, if there is anything
            enabled = [i for i, elem in enumerate(elements) if elem not in self.disabled]
            if enabled:
                self.default_index = enabled[0]

    def select(self) -> str:
        print(EscapeCodes.fg(*ORANGE) + f"Select{' ' + self.message if self.message else ''}:" + EscapeCodes.reset)
        print(EscapeCodes.hide_cursor, end="")

        for elem in self.elements:
            print(" ", " " * self.cursor_len, " ", self._render(elem), sep="")
        print(EscapeCodes.up(self.num) + EscapeCodes.right(1), end="")

        current = self.default_index
        prev_current = current

        if current:
            print(EscapeCodes.down(current), end="")
        print(self.cursor + EscapeCodes.left(self.cursor_len), end="")
        sys.stdout.flush()

        while True:
            c = getkey()
            if c in (UnixKeys.up, WindowsKeys.up, "k"):
                current -= 1
            elif c in (UnixKeys.down, WindowsKeys.down, "j"):
                current += 1
            elif c == "\r":
                if self.elements[current] in self.disabled:
                    self._cleanup(current)
                    raise DisabledSelection(self.elements[current], self.disabled[self.elements[current]])
                break
            else:
                self._cleanup(current)
                raise SelectionInterrupt
            current %= self.num

            if current != prev_current:
                move = EscapeCodes.down(current - prev_current) if current > prev_current else EscapeCodes.up(prev_current - current)
                prev_current = current

                print(" " * self.cursor_len + EscapeCodes.left(self.cursor_len), end="")
                print(move, end="")
                print(self.cursor + EscapeCodes.left(self.cursor_len), end="")
                sys.stdout.flush()

        self._cleanup(current)
        return self.elements[current]

    def _render(self, elem: str) -> str:
        if elem not in self.disabled:
            return elem

        # keep each entry on a single line, otherwise cursor movement gets out of sync
        width = shutil.get_terminal_size().columns - (self.cursor_len + 2)
        text = elem
        note = self.disabled[elem]
        if note:
            text = f"{elem} ({note})"
        if len(text) > width:
            text = text[: max(width - 3, 0)] + "..."
        return EscapeCodes.dim + text + EscapeCodes.reset

    def _cleanup(self, current: int) -> None:
        print(EscapeCodes.up(current + 1) + EscapeCodes.line_begin, end="")
        print(EscapeCodes.clear_after_cursor, end="")
        print(EscapeCodes.show_cursor, end="")
        sys.stdout.flush()
