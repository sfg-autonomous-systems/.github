from __future__ import annotations

import copy
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from sfg_contribution_tooling import constants, files, jsonc
from sfg_contribution_tooling.errors import Error, UnexpectedTypeError
from sfg_contribution_tooling.vscode.file_kind import FileKind

if TYPE_CHECKING:
    from pathlib import Path

    from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


class VsCodeFile:
    """A settings.json, extensions.json or devcontainer.json file.

    Keeps the whole document and only changes its settings and extensions sections, as a
    devcontainer.json or a settings.json holds much more than those.
    """

    def __init__(
        self, filepath: Path, kind: FileKind, data: Any, has_comments: bool
    ) -> None:
        self.filepath = filepath
        self.kind = kind
        self.data = data
        self.has_comments = has_comments

        # The formatted text to write, set when the file is created or merged.
        self._text: str | None = None
        self._created = False

    @classmethod
    def load(cls, filepath: Path) -> VsCodeFile:
        kind = FileKind.from_path(filepath)

        text = files.read_text(filepath)

        try:
            data, has_comments = jsonc.parse(text)
        except Error as error:
            raise Error(f"{os.path.relpath(filepath)}: {error}") from None

        return cls(filepath, kind, data, has_comments)

    @classmethod
    def create(cls, filepath: Path, vscode_setup: VsCodeSetup) -> VsCodeFile:
        """Build a new settings.json or extensions.json in memory from the setup.

        Args:
            filepath: Where the file is to be written. Its name sets the kind of file.
            vscode_setup: Setup providing the settings or extensions.

        Returns:
            The file, formatted and ready to write.

        Raises:
            Error: If the file is not named settings.json or extensions.json, or dprint
                cannot be run or fails.
        """
        kind = FileKind.from_path(filepath)

        match kind:
            case FileKind.Settings:
                text = vscode_setup.settings_to_string()
            case FileKind.Extensions:
                text = vscode_setup.extensions_to_string()
            case FileKind.Devcontainer:
                raise Error(f"{os.path.relpath(filepath)}: cannot be created")

        data, _ = jsonc.parse(text)
        file = cls(filepath, kind, data, has_comments=False)
        file._text = file._format(text)
        file._created = True

        return file

    def find_differences(self, vscode_setup: VsCodeSetup) -> list[str]:
        """List the settings and extensions the file lacks or sets differently.

        Differences read 'key: difference'; settings objects are compared key by key.

        Args:
            vscode_setup: Setup to compare the file with.

        Returns:
            The differences, or only the type error if the file or one of its sections
            or their parents has another type.
        """
        try:
            settings, extensions = self._get_sections(create=False)
        except UnexpectedTypeError as error:
            return [str(error)]

        differences = []

        if settings is not None and self.kind.settings_path is not None:
            differences.extend(
                self._find_setting_differences(
                    settings, vscode_setup.settings, self.kind.settings_path
                )
            )

        if extensions is not None and self.kind.extensions_path is not None:
            key_path = jsonc.format_key_path(self.kind.extensions_path)
            differences.extend(
                f"{key_path}: missing {jsonc.format_value(extension)}"
                for extension in self._find_missing_extensions(extensions, vscode_setup)
            )

        return differences

    def merge_from(self, vscode_setup: VsCodeSetup) -> None:
        """Merge the setup into the sections, the setup winning every difference.

        Args:
            vscode_setup: Setup to merge into the file.

        Raises:
            Error: If the file or one of its sections or their parents has another type,
                or dprint cannot be run or fails.
        """
        try:
            settings, extensions = self._get_sections(create=True)
        except UnexpectedTypeError as error:
            raise Error(f"{os.path.relpath(self.filepath)}: {error}") from None

        if settings is not None:
            self._merge_settings(settings, vscode_setup.settings)

        if extensions is not None:
            extensions.extend(self._find_missing_extensions(extensions, vscode_setup))

        self._text = self._format(jsonc.dump(self.data) + "\n")

    def report(self, differences: list[str]) -> None:
        for difference in differences:
            print(f"{os.path.relpath(self.filepath)}: {difference}", file=sys.stderr)

    def write(self) -> None:
        """Write the file if it was created or merged, noting any comments it lost.

        Raises:
            Error: If the file cannot be written.
        """
        if self._text is None:
            return

        if self._created:
            files.write(self.filepath, self._text, "Created")
        else:
            note = " and removed its comments" if self.has_comments else ""
            files.write(self.filepath, self._text, "Updated", note)

    def _get_sections(
        self, create: bool
    ) -> tuple[dict[str, Any] | None, list[Any] | None]:
        """Return the settings object and the extensions array of the file.

        Args:
            create: Whether to add missing sections and their missing parents.

        Returns:
            The settings object and the extensions array, each None if the kind of file
            does not have it. A missing section that is not added is returned empty.

        Raises:
            UnexpectedTypeError: If the file is not an object, or a section or one of
                its parents has another type.
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
        """Return the section at the key path, checking its type and parent types.

        Args:
            key_path: Keys leading to the section.
            section_type: Expected type of the section. Its parents must be objects.
            create: Whether to add a missing section and its missing parents.

        Returns:
            The section. A missing section that is not added is returned empty.

        Raises:
            UnexpectedTypeError: If the section or one of its parents has another type.
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
        """Format the text with the packaged dprint, so it matches format on save.

        Args:
            text: JSON text of the file.

        Returns:
            The formatted text.

        Raises:
            Error: If dprint cannot be run or fails.
        """
        # The bare file name keeps the includes and excludes
        # of dprint.jsonc from skipping the file.
        command = [
            str(constants.DPRINT_BINARY),
            "fmt",
            "--stdin",
            self.filepath.name,
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
                f"{os.path.relpath(self.filepath)}: dprint failed: {result.stderr.strip()}"
            )

        return result.stdout

    @staticmethod
    def _find_missing_extensions(
        extensions: list[Any], vscode_setup: VsCodeSetup
    ) -> list[str]:
        present = {
            extension.lower() for extension in extensions if isinstance(extension, str)
        }
        return [
            extension
            for extension in vscode_setup.extensions
            if extension.lower() not in present
        ]

    @staticmethod
    def _find_setting_differences(
        settings: dict[str, Any], reference: dict[str, Any], key_path: tuple[str, ...]
    ) -> list[str]:
        """List the settings that are missing or differ in value.

        Objects are compared key by key.

        Args:
            settings: Settings of the file.
            reference: Settings to compare with.
            key_path: Key path of the settings in the file, which the keys in the
                differences start with.

        Returns:
            The differences, each reading 'key: difference'.
        """
        differences = []

        for key, value in reference.items():
            value_path = (*key_path, key)

            if key not in settings:
                differences.append(f"{jsonc.format_key_path(value_path)}: missing")
            elif isinstance(settings[key], dict) and isinstance(value, dict):
                differences.extend(
                    VsCodeFile._find_setting_differences(
                        settings[key], value, value_path
                    )
                )
            elif not jsonc.are_equal(settings[key], value):
                differences.append(
                    f"{jsonc.format_key_path(value_path)}: "
                    f"{jsonc.format_value(settings[key])}, expected {jsonc.format_value(value)}"
                )

        return differences

    @staticmethod
    def _merge_settings(settings: dict[str, Any], reference: dict[str, Any]) -> None:
        """Merge the reference into the settings.

        Objects are merged key by key, other values are replaced as a whole.

        Args:
            settings: Settings to merge into, changed in place.
            reference: Settings to merge.
        """
        for key, value in reference.items():
            if isinstance(settings.get(key), dict) and isinstance(value, dict):
                VsCodeFile._merge_settings(settings[key], value)
            else:
                settings[key] = copy.deepcopy(value)
