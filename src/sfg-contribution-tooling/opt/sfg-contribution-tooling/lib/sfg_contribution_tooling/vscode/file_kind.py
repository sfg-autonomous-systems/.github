from __future__ import annotations

import enum
import os
from typing import TYPE_CHECKING

from sfg_contribution_tooling.error import Error

if TYPE_CHECKING:
    from pathlib import Path


class FileKind(enum.Enum):
    """The kind of a VS Code file, which sets where its settings and extensions go."""

    Settings = "settings"
    Extensions = "extensions"
    Devcontainer = "devcontainer"

    @property
    def settings_path(self) -> tuple[str, ...] | None:
        """Return the key path of the settings object, or None if the file has no settings."""
        return _SETTINGS_PATHS.get(self)

    @property
    def extensions_path(self) -> tuple[str, ...] | None:
        """Return the key path of the extensions array, or None if the file has no extensions."""
        return _EXTENSIONS_PATHS.get(self)

    @classmethod
    def from_path(cls, path: Path) -> FileKind:
        """Return the kind of a file by its name."""
        try:
            return _FILE_NAMES[path.name]
        except KeyError:
            raise Error(
                f"{os.path.relpath(path)}: expected a file named "
                "settings.json, extensions.json, devcontainer.json or .devcontainer.json"
            ) from None


_FILE_NAMES = {
    "settings.json": FileKind.Settings,
    "extensions.json": FileKind.Extensions,
    "devcontainer.json": FileKind.Devcontainer,
    ".devcontainer.json": FileKind.Devcontainer,
}
_SETTINGS_PATHS: dict[FileKind, tuple[str, ...]] = {
    FileKind.Settings: (),
    FileKind.Devcontainer: ("customizations", "vscode", "settings"),
}
_EXTENSIONS_PATHS: dict[FileKind, tuple[str, ...]] = {
    FileKind.Extensions: ("recommendations",),
    FileKind.Devcontainer: ("customizations", "vscode", "extensions"),
}
