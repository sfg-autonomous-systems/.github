from __future__ import annotations

import enum
import os
from typing import TYPE_CHECKING

from sfg_contribution_tooling.errors import Error

if TYPE_CHECKING:
    from pathlib import Path


class FileKind(enum.Enum):
    """The kind of a VS Code file, which sets where its settings and extensions go."""

    Settings = "settings"
    Extensions = "extensions"
    Devcontainer = "devcontainer"

    @property
    def settings_path(self) -> tuple[str, ...] | None:
        """Return the key path of the settings object, or None if there is none."""
        match self:
            case FileKind.Settings:
                return ()
            case FileKind.Extensions:
                return None
            case FileKind.Devcontainer:
                return ("customizations", "vscode", "settings")

    @property
    def extensions_path(self) -> tuple[str, ...] | None:
        """Return the key path of the extensions array, or None if there is none."""
        match self:
            case FileKind.Settings:
                return None
            case FileKind.Extensions:
                return ("recommendations",)
            case FileKind.Devcontainer:
                return ("customizations", "vscode", "extensions")

    @classmethod
    def from_path(cls, filepath: Path) -> FileKind:
        """Return the kind of a file by its name.

        Args:
            filepath: The file, of which only the name is used.

        Returns:
            The kind matching the file name.

        Raises:
            Error: If the name is not settings.json, extensions.json, devcontainer.json
                or .devcontainer.json.
        """
        match filepath.name:
            case "settings.json":
                return FileKind.Settings
            case "extensions.json":
                return FileKind.Extensions
            case "devcontainer.json" | ".devcontainer.json":
                return FileKind.Devcontainer
            case _:
                raise Error(
                    f"{os.path.relpath(filepath)}: expected a file named "
                    "settings.json, extensions.json, devcontainer.json or .devcontainer.json"
                )
