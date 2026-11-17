from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sfg_contribution_tooling import constants, jsonc
from sfg_contribution_tooling.error import Error

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sfg_contribution_tooling.language_setup import LanguageSetup


@dataclass
class VsCodeSetup:
    """The settings and extensions that VS Code files get.

    'sections' holds the name and the settings of each language, for the '// <name> Settings'
    comments of a created settings.json. 'settings' holds the settings of all of them combined.
    """

    sections: list[tuple[str, dict[str, Any]]]
    extensions: list[str]
    settings: dict[str, Any]

    @classmethod
    def combine(cls, setups: Iterable[LanguageSetup]) -> VsCodeSetup:
        """Combine the VS Code setups, failing on a setting that languages give different values.

        Extension IDs are case-insensitive, so an extension of several languages is added once.
        """
        sections: list[tuple[str, dict[str, Any]]] = []
        extensions: dict[str, str] = {}
        settings: dict[str, Any] = {}
        origins: dict[tuple[str, ...], str] = {}

        for setup in setups:
            if setup.vscode is None:
                continue

            sections.extend(setup.vscode.sections)

            for extension in setup.vscode.extensions:
                extensions.setdefault(extension.lower(), extension)

            _add_settings(settings, setup.vscode.settings, (), setup.key, origins)

        return cls(sections, list(extensions.values()), settings)

    def render_settings(self) -> str:
        """Serialize a created settings.json with a comment above the settings of each language.

        Settings that languages give different values, which are merged objects such as
        'files.exclude', go under the settings of the first language, which is the general one. A
        setting that several languages repeat with the same value, such as 'dprint.path', goes
        under the first of them.
        """
        values: dict[str, list[Any]] = {}

        for _, settings in self.sections:
            for key, value in settings.items():
                values.setdefault(key, []).append(value)

        first_settings = self.sections[0][1] if self.sections else {}
        first_keys = {
            key
            for key, key_values in values.items()
            if key in first_settings
            or any(not jsonc.same_value(value, key_values[0]) for value in key_values)
        }
        written_keys = set(first_keys)
        ordered_settings: dict[str, Any] = {}
        comments: dict[str, str] = {}

        for index, (name, settings) in enumerate(self.sections):
            if index == 0:
                keys = [key for key in self.settings if key in first_keys]
            else:
                keys = [key for key in settings if key not in written_keys]
                written_keys.update(keys)

            if not keys:
                continue

            comments[keys[0]] = f"{name} Settings"
            ordered_settings.update((key, self.settings[key]) for key in keys)

        return jsonc.dump(ordered_settings, comments=comments) + "\n"

    def render_extensions(self) -> str:
        return jsonc.dump({"recommendations": self.extensions}) + "\n"


def _add_settings(
    target: dict[str, Any],
    source: dict[str, Any],
    key_path: tuple[str, ...],
    language: str,
    origins: dict[tuple[str, ...], str],
) -> None:
    """Add the settings of one language, failing on a value another language sets differently."""
    for key, value in source.items():
        value_path = (*key_path, key)

        if key not in target:
            target[key] = copy.deepcopy(value)
            origins[value_path] = language
        elif isinstance(target[key], dict) and isinstance(value, dict):
            _add_settings(target[key], value, value_path, language, origins)
        elif not jsonc.same_value(target[key], value):
            # The value came from the language that added it or one of its parent objects.
            origin = next(
                origins[value_path[:length]]
                for length in range(len(value_path), 0, -1)
                if value_path[:length] in origins
            )
            raise Error(
                f"{constants.LANGUAGE_SETUPS_FILE}: {jsonc.format_key_path(value_path)}: "
                f"'{origin}' and '{language}' have different values"
            )
