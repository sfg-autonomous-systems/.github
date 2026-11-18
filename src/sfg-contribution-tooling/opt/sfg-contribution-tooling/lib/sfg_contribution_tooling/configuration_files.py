from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from sfg_contribution_tooling import constants, files

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from sfg_contribution_tooling.language_setup import LanguageSetup


class ConfigurationFiles:
    """Names of configuration files in /opt/sfg-contribution-tooling/share/config/."""

    def __init__(self, names: Iterable[str]) -> None:
        self.names = list(dict.fromkeys(names))

    @classmethod
    def combine(cls, language_setups: Iterable[LanguageSetup]) -> ConfigurationFiles:
        """Combine the configuration files of the language setups, each name once.

        Args:
            language_setups: Setups whose configuration files to combine.

        Returns:
            The configuration files, in the order of the setups.
        """
        return cls(
            name
            for language_setup in language_setups
            for name in language_setup.configuration_files.names
        )

    def install(self, directory: Path) -> None:
        """Copy the missing files into the directory and warn about differing ones.

        Repositories may adjust their configuration files, so differences are only
        warnings. Every file is read before any is written, so a file that cannot be
        read leaves the directory unchanged.

        Args:
            directory: Repository root to copy the files into.

        Raises:
            Error: If a file cannot be read or written.
        """
        missing: dict[Path, bytes] = {}

        for name in self.names:
            source = constants.CONFIG_DIRECTORY / name
            target = directory / name
            content = files.read_bytes(source)

            if not target.exists():
                missing[target] = content
            elif files.read_bytes(target) != content:
                print(
                    f"{os.path.relpath(target)}: differs from {source}", file=sys.stderr
                )

        for target, content in missing.items():
            files.write(target, content, "Created")
