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
    def read(cls, filepath: Path) -> LanguageSetups:
        """Read the data file and check that its language setups can be combined.

        Args:
            filepath: Data file to read.

        Returns:
            The language setups, the general setup first.

        Raises:
            Error: If the file cannot be read or parsed, has no general setup, or its
                language setups are invalid or cannot be combined.
        """
        text = files.read_text(filepath)

        try:
            raw_setups, _ = jsonc.parse(text)
        except Error as error:
            raise Error(f"{os.path.relpath(filepath)}: {error}") from None

        if not isinstance(raw_setups, dict) or cls._GENERAL_KEY not in raw_setups:
            raise Error(
                f"{filepath}: expected an object with a '{cls._GENERAL_KEY}' entry"
            )

        try:
            setups = [
                LanguageSetup.from_raw(key, raw_setup)
                for key, raw_setup in raw_setups.items()
            ]
        except Error as error:
            raise Error(f"{filepath}: {error}") from None

        # The general setup comes first wherever it is in the data file.
        setups.sort(key=lambda setup: setup.key != cls._GENERAL_KEY)

        # Combines all language setups once, so a conflict fails regardless of which
        # languages are chosen.
        VsCodeSetup.combine(setups)

        return cls(setups)

    def get_selectable_keys(self) -> list[str]:
        """Return the keys of the language setups the --languages option can choose.

        Returns:
            The keys of all language setups except the general one, in their order.
        """
        return [setup.key for setup in self._setups[1:]]

    def select(self, chosen: list[str] | None) -> LanguageSetups:
        """Return the general setup and the chosen language setups.

        Args:
            chosen: Keys of the chosen language setups, or None to choose all.

        Returns:
            The selected language setups, in their order.
        """
        return LanguageSetups(
            [
                setup
                for setup in self._setups
                if setup is self.general or chosen is None or setup.key in chosen
            ]
        )
