from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sfg_contribution_tooling import jsonc
from sfg_contribution_tooling.configuration_files import ConfigurationFiles
from sfg_contribution_tooling.errors import Error
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


@dataclass
class LanguageSetup:
    """The configuration files and IDE setups of one entry of the data file."""

    key: str
    name: str
    configuration_files: ConfigurationFiles
    vscode: VsCodeSetup | None

    @classmethod
    def from_raw(cls, key: str, raw_setup: Any) -> LanguageSetup:
        """Create the setup from raw data, raising an Error without the path if it is invalid."""
        name = cls._get_value(key, raw_setup, ("name",), str)
        configuration_files = cls._get_value(key, raw_setup, ("configurationFiles",), list)
        vscode = None

        if cls._get_value(key, raw_setup, ("ides",), dict, required=False) is not None:
            vscode = cls._get_value(key, raw_setup, ("ides", "vscode"), dict, required=False)

        if vscode is not None:
            extensions = cls._get_value(key, raw_setup, ("ides", "vscode", "extensions"), list)
            settings = cls._get_value(key, raw_setup, ("ides", "vscode", "settings"), dict)
            vscode = VsCodeSetup([(name, settings)], extensions, settings)

        return cls(key, name, ConfigurationFiles(configuration_files), vscode)

    @staticmethod
    def _get_value(
        key: str,
        raw_setup: Any,
        key_path: tuple[str, ...],
        value_type: type,
        *,
        required: bool = True,
    ) -> Any:
        """Return the value at the key path of a raw setup, whose parents must have been checked before.

        Returns None for a missing value that is not required. The items of an array must be strings.
        """
        if not isinstance(raw_setup, dict):
            raise Error(
                f"{key}: invalid setup: expected an object, found {jsonc.describe_type(raw_setup)}"
            )

        value: Any = raw_setup

        for path_key in key_path:
            if path_key not in value:
                if required:
                    raise Error(
                        f"{key}: invalid setup: {jsonc.format_key_path(key_path)}: missing"
                    )

                return None

            value = value[path_key]

        if not isinstance(value, value_type):
            found = jsonc.describe_type(value)
        elif isinstance(value, list) and not all(isinstance(item, str) for item in value):
            found = "an array with other items than strings"
        else:
            return value

        raise Error(
            f"{key}: invalid setup: {jsonc.format_key_path(key_path)}: "
            f"expected {jsonc.describe_type(value_type())}, found {found}"
        )
