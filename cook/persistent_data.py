"""
Persistent user data storage.

Stores JSON data in:

    ~/.config/<app_name>/<filename>

The module is intentionally dependency-free and uses only the Python
standard library.

Filesystem errors are reported to stderr and do not normally propagate
to the caller. If persistence fails, the in-memory data continues to
be usable for the lifetime of the process.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


class PersistentData:
    """Simple persistent JSON-backed key/value storage."""

    def __init__(
        self,
        app_name: str,
        defaults: dict[str, Any] | None = None,
        filename: str = "data.json",
    ) -> None:
        self.app_name = app_name
        self.defaults = dict(defaults or {})
        self.filename = filename

        self.config_dir = Path.home() / ".config" / app_name
        self.path = self.config_dir / filename

        self.data: dict[str, Any] = dict(self.defaults)

        self.load()

    def _error(self, message: str, exc: Exception) -> None:
        """Print a filesystem/storage error without raising it."""
        print(
            f"{self.app_name}: {message}: {exc}",
            file=sys.stderr,
        )

    def load(self) -> None:
        """
        Load data from disk.

        If the file does not exist, defaults are used and the file is
        created. If loading fails, defaults/current data are retained.
        """
        if not self.path.exists():
            self.data = dict(self.defaults)
            self.save()
            return

        try:
            with self.path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)

            if not isinstance(loaded, dict):
                raise ValueError("top-level JSON value must be an object")

            # Start with defaults so newly introduced settings get their
            # default value even when an older file is being loaded.
            self.data = dict(self.defaults)
            self.data.update(loaded)

        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self._error(f"could not read {self.path}", exc)

    def save(self) -> bool:
        """
        Save the current data to disk.

        Uses a temporary file followed by os.replace() so a failure during
        writing does not normally corrupt an existing data file.

        Returns True on success, False on failure.
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Create the temporary file in the same directory. This makes
            # os.replace() atomic on normal local filesystems.
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{self.filename}.",
                suffix=".tmp",
                dir=self.config_dir,
                text=True,
            )

            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(
                        self.data,
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())

                os.replace(temp_name, self.path)

            except Exception:
                # The descriptor may already have been closed. Remove the
                # temporary file if it still exists.
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
                raise

            return True

        except (OSError, TypeError, ValueError) as exc:
            self._error(f"could not write {self.path}", exc)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting, or default if it does not exist."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set a value.

        By default the value is immediately persisted to disk.

        Returns True if the value was persisted successfully, or False if
        saving failed. The in-memory value is updated even when saving fails.
        """
        self.data[key] = value

        if save:
            return self.save()

        return True

    def update(self, values: dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple values.

        By default all values are persisted with a single write.
        """
        self.data.update(values)

        if save:
            return self.save()

        return True

    def delete(self, key: str, save: bool = True) -> bool:
        """Delete a setting if it exists."""
        self.data.pop(key, None)

        if save:
            return self.save()

        return True

    def reset(self, save: bool = True) -> bool:
        """Reset all settings to their defaults."""
        self.data = dict(self.defaults)

        if save:
            return self.save()

        return True

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!s})"


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    settings = PersistentData(
        "mytool",
        defaults={
            "color": True,
            "theme": "dark",
            "recent_files": [],
        },
    )

    print(settings.get("theme"))

    settings["theme"] = "light"
    settings.set("color", False)

    print(settings.data)
