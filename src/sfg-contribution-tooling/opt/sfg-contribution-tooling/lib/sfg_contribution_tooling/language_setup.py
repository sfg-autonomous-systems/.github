from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sfg_contribution_tooling import jsonc
from sfg_contribution_tooling.configuration_files import ConfigurationFiles
from sfg_contribution_tooling.error import Error
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


@dataclass
class LanguageSetup:
    """The configuration files and IDE setups of one entry of the data file."""

    key: str
    name: str
    configuration_files: ConfigurationFiles
    vscode: VsCodeSetup | None

    @classmethod
    def from_entry(cls, key: str, entry: Any) -> LanguageSetup:
        """Create the setup of an entry, raising an Error without the path if it is invalid."""
        name = _get_value(key, entry, ("name",), str)
        configuration_files = _get_value(key, entry, ("configurationFiles",), list)
        vscode = None

        if _get_value(key, entry, ("ides",), dict, required=False) is not None:
            vscode = _get_value(key, entry, ("ides", "vscode"), dict, required=False)

        if vscode is not None:
            extensions = _get_value(key, entry, ("ides", "vscode", "extensions"), list)
            settings = _get_value(key, entry, ("ides", "vscode", "settings"), dict)
            vscode = VsCodeSetup([(name, settings)], extensions, settings)

        return cls(key, name, ConfigurationFiles(configuration_files), vscode)


def _get_value(
    key: str,
    entry: Any,
    key_path: tuple[str, ...],
    value_type: type,
    *,
    required: bool = True,
) -> Any:
    """Return the value at the key path of an entry, whose parents must have been checked before.

    Returns None for a missing value that is not required. The items of an array must be strings.
    """
    if not isinstance(entry, dict):
        raise Error(
            f"{key}: invalid entry: expected an object, found {jsonc.describe_type(entry)}"
        )

    value: Any = entry

    for path_key in key_path:
        if path_key not in value:
            if required:
                raise Error(
                    f"{key}: invalid entry: {jsonc.format_key_path(key_path)}: missing"
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
        f"{key}: invalid entry: {jsonc.format_key_path(key_path)}: "
        f"expected {jsonc.describe_type(value_type())}, found {found}"
    )
