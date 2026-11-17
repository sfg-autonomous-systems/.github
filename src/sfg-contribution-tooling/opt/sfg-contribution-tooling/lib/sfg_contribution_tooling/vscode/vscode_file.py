from __future__ import annotations

import copy
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from sfg_contribution_tooling import constants, files, jsonc
from sfg_contribution_tooling.error import Error
from sfg_contribution_tooling.vscode.file_kind import FileKind
from sfg_contribution_tooling.vscode.unexpected_type_error import UnexpectedTypeError

if TYPE_CHECKING:
    from pathlib import Path

    from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


class VsCodeFile:
    """A settings.json, extensions.json or devcontainer.json file.

    Keeps the whole document and only changes its settings and extensions sections, as a
    devcontainer.json or a settings.json holds much more than those.
    """

    def __init__(
        self, path: Path, kind: FileKind, data: Any, has_comments: bool
    ) -> None:
        self.path = path
        self.kind = kind
        self.data = data
        self.has_comments = has_comments

        # The formatted text to write, set when the file is created or merged.
        self._text: str | None = None
        self._created = False

    @classmethod
    def load(cls, path: Path) -> VsCodeFile:
        kind = FileKind.from_path(path)

        text = files.read_text(path)

        try:
            data, has_comments = jsonc.parse(text)
        except Error as error:
            raise Error(f"{os.path.relpath(path)}: {error}") from None

        return cls(path, kind, data, has_comments)

    @classmethod
    def create(cls, path: Path, setup: VsCodeSetup) -> VsCodeFile:
        """Render a missing settings.json or extensions.json from the setup, without writing it."""
        kind = FileKind.from_path(path)

        if kind is FileKind.Settings:
            text = setup.settings_to_string()
        elif kind is FileKind.Extensions:
            text = setup.extensions_to_string()
        else:
            raise Error(f"{os.path.relpath(path)}: cannot be created")

        data, _ = jsonc.parse(text)
        file = cls(path, kind, data, has_comments=False)
        file._text = file._format(text)
        file._created = True

        return file

    def find_differences(self, setup: VsCodeSetup) -> list[str]:
        """List the settings and extensions of the setup that the file lacks or sets differently.

        Each difference is given as 'key: difference', settings objects are compared key by key.
        """
        try:
            settings, extensions = self._get_sections(create=False)
        except UnexpectedTypeError as error:
            return [str(error)]

        differences = []

        if settings is not None and self.kind.settings_path is not None:
            differences.extend(
                _find_setting_differences(settings, setup.settings, self.kind.settings_path)
            )

        if extensions is not None and self.kind.extensions_path is not None:
            key_path = jsonc.format_key_path(self.kind.extensions_path)
            differences.extend(
                f"{key_path}: missing {jsonc.format_value(extension)}"
                for extension in _find_missing_extensions(extensions, setup)
            )

        return differences

    def merge_from(self, setup: VsCodeSetup) -> None:
        """Merge the setup into the sections, the setup winning every difference."""
        try:
            settings, extensions = self._get_sections(create=True)
        except UnexpectedTypeError as error:
            raise Error(f"{os.path.relpath(self.path)}: {error}") from None

        if settings is not None:
            _merge_settings(settings, setup.settings)

        if extensions is not None:
            extensions.extend(_find_missing_extensions(extensions, setup))

        self._text = self._format(jsonc.dump(self.data) + "\n")

    def report(self, differences: list[str]) -> None:
        for difference in differences:
            print(f"{os.path.relpath(self.path)}: {difference}", file=sys.stderr)

    def write(self) -> None:
        """Write the file if it was created or merged, noting whether it lost its comments."""
        if self._text is None:
            return

        if self._created:
            files.write(self.path, self._text, "Created")
        else:
            note = " and removed its comments" if self.has_comments else ""
            files.write(self.path, self._text, "Updated", note)

    def _get_sections(self, create: bool) -> tuple[dict[str, Any] | None, list[Any] | None]:
        """Return the settings object and the extensions array of the file.

        Each is None if the kind of file does not have it.
        """
        if not isinstance(self.data, dict):
            raise UnexpectedTypeError(
                f"expected an object, found {jsonc.describe_type(self.data)}"
            )

        settings = None
        extensions = None

        if self.kind.settings_path is not None:
            settings = self._get_section(self.kind.settings_path, dict, create)

        if self.kind.extensions_path is not None:
            extensions = self._get_section(self.kind.extensions_path, list, create)

        return settings, extensions

    def _get_section(
        self, key_path: tuple[str, ...], section_type: type, create: bool
    ) -> Any:
        """Return the section at the key path, checking its type and the types of its parents.

        A missing section and its missing parents are added if 'create' is set, and returned empty
        otherwise.
        """
        section: Any = self.data

        for depth, key in enumerate(key_path):
            expected_type = section_type if depth == len(key_path) - 1 else dict

            if key not in section:
                value = expected_type()

                if create:
                    section[key] = value
            else:
                value = section[key]

                if not isinstance(value, expected_type):
                    raise UnexpectedTypeError(
                        f"{jsonc.format_key_path(key_path[: depth + 1])}: "
                        f"expected {jsonc.describe_type(expected_type())}, "
                        f"found {jsonc.describe_type(value)}"
                    )

            section = value

        return section

    def _format(self, text: str) -> str:
        """Format the text with the packaged dprint, so it matches format on save."""
        # The bare file name keeps the includes and excludes of dprint.jsonc from skipping the file.
        command = [
            str(constants.DPRINT_BINARY),
            "fmt",
            "--stdin",
            self.path.name,
            "--config",
            str(constants.CONFIG_DIRECTORY / "dprint.jsonc"),
        ]

        try:
            result = subprocess.run(
                command, input=text, capture_output=True, encoding="utf-8", check=False
            )
        except OSError as error:
            raise Error(
                f"{constants.DPRINT_BINARY}: {files.describe_error(error)}"
            ) from None

        if result.returncode != 0:
            raise Error(
                f"{os.path.relpath(self.path)}: dprint failed: {result.stderr.strip()}"
            )

        return result.stdout


def _find_missing_extensions(extensions: list[Any], setup: VsCodeSetup) -> list[str]:
    present = {
        extension.lower() for extension in extensions if isinstance(extension, str)
    }
    return [
        extension for extension in setup.extensions if extension.lower() not in present
    ]


def _find_setting_differences(
    settings: dict[str, Any], reference: dict[str, Any], key_path: tuple[str, ...]
) -> list[str]:
    """List the settings that are missing or have another value, comparing objects key by key."""
    differences = []

    for key, value in reference.items():
        value_path = (*key_path, key)

        if key not in settings:
            differences.append(f"{jsonc.format_key_path(value_path)}: missing")
        elif isinstance(settings[key], dict) and isinstance(value, dict):
            differences.extend(_find_setting_differences(settings[key], value, value_path))
        elif not jsonc.are_equal(settings[key], value):
            differences.append(
                f"{jsonc.format_key_path(value_path)}: "
                f"{jsonc.format_value(settings[key])}, expected {jsonc.format_value(value)}"
            )

    return differences


def _merge_settings(settings: dict[str, Any], reference: dict[str, Any]) -> None:
    """Merge the reference into the settings: objects key by key, other values as a whole."""
    for key, value in reference.items():
        if isinstance(settings.get(key), dict) and isinstance(value, dict):
            _merge_settings(settings[key], value)
        else:
            settings[key] = copy.deepcopy(value)
