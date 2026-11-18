from __future__ import annotations

import os
from typing import TYPE_CHECKING

from sfg_contribution_tooling import files, jsonc
from sfg_contribution_tooling.errors import Error
from sfg_contribution_tooling.language_setup import LanguageSetup
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class LanguageSetups:
    """Language setups in the order of the data file, the general setup first."""

    _GENERAL_KEY = "general"

    @property
    def general(self) -> LanguageSetup:
        return self._setups[0]

    def __init__(self, setups: list[LanguageSetup]) -> None:
        self._setups = setups

    def __iter__(self) -> Iterator[LanguageSetup]:
        return iter(self._setups)

    @classmethod
    def read(cls, path: Path) -> LanguageSetups:
        """Read the data file and check that its setups can be combined."""
        text = files.read_text(path)

        try:
            data, _ = jsonc.parse(text)
        except Error as error:
            raise Error(f"{os.path.relpath(path)}: {error}") from None

        if not isinstance(data, dict) or cls._GENERAL_KEY not in data:
            raise Error(f"{path}: expected an object with a '{cls._GENERAL_KEY}' entry")

        try:
            setups = [
                LanguageSetup.from_raw(key, raw_setup) for key, raw_setup in data.items()
            ]
        except Error as error:
            raise Error(f"{path}: {error}") from None

        # The general setup comes first wherever it is in the data file.
        setups.sort(key=lambda setup: setup.key != cls._GENERAL_KEY)

        # Combines all setups once, so a conflict fails regardless of which languages are chosen.
        VsCodeSetup.combine(setups)

        return cls(setups)

    def list_selectable_keys(self) -> list[str]:
        """Return the keys of the setups the --languages option can choose."""
        return [setup.key for setup in self._setups[1:]]

    def select(self, chosen: list[str] | None) -> LanguageSetups:
        """Return the general setup and the chosen setups, or all setups if none are chosen."""
        return LanguageSetups(
            [
                setup
                for setup in self._setups
                if setup is self.general or chosen is None or setup.key in chosen
            ]
        )
