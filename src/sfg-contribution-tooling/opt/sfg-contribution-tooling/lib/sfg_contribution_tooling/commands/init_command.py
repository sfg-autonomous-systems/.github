from __future__ import annotations

import os
import shlex
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from sfg_contribution_tooling import constants
from sfg_contribution_tooling.commands.command import Command
from sfg_contribution_tooling.configuration_files import ConfigurationFiles
from sfg_contribution_tooling.errors import Error
from sfg_contribution_tooling.vscode.extension_installer import ExtensionInstaller
from sfg_contribution_tooling.vscode.file_kind import FileKind
from sfg_contribution_tooling.vscode.vscode_file import VsCodeFile
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup

if TYPE_CHECKING:
    import argparse

    from sfg_contribution_tooling.language_setups import LanguageSetups


class InitCommand(Command):
    """Sets up the configuration and VS Code files of a repository, never changing existing ones."""

    name = "init"
    help = (
        "create the missing configuration and VS Code files and check the existing ones"
    )
    description = textwrap.dedent("""\
        Copies the configuration files of the chosen languages into the directory and
        creates .vscode/settings.json and .vscode/extensions.json. Sets up all
        languages unless --languages is given.

        Never changes existing files, only checks them. For a configuration file that
        differs, prints a warning naming the reference to compare it with. For VS Code
        files that differ, prints the update command to run and exits with status 1.

        After creating .vscode/extensions.json, offers to install the extensions.
    """)

    def __init__(self, setups: LanguageSetups) -> None:
        self._setups = setups

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "directory",
            nargs="?",
            default=".",
            help="repository root (default: current directory)",
        )
        self._add_languages_argument(
            parser, self._setups.list_selectable_keys(), "languages to set up"
        )

    def run(self, args: argparse.Namespace) -> int:
        directory = Path(args.directory)

        if not directory.is_dir():
            raise Error(f"{os.path.relpath(directory)}: not a directory")

        selected = self._setups.select(args.languages)
        configuration_files = ConfigurationFiles.combine(selected)
        vscode = VsCodeSetup.combine(selected)
        created_files: list[VsCodeFile] = []
        differing_files: list[tuple[VsCodeFile, list[str]]] = []

        # Loads and renders the VS Code files before writing any file, so a failure leaves all
        # unchanged.
        for name in ("settings.json", "extensions.json"):
            path = directory / ".vscode" / name

            if not path.exists():
                created_files.append(VsCodeFile.create(path, vscode))
                continue

            file = VsCodeFile.load(path)
            differences = file.find_differences(vscode)

            if differences:
                differing_files.append((file, differences))

        configuration_files.install(directory)

        for file, differences in differing_files:
            file.report(differences)

        for file in created_files:
            file.write()

        if any(file.kind is FileKind.Extensions for file in created_files):
            ExtensionInstaller(vscode).offer()

        if not differing_files:
            return 0

        command = [
            constants.PROGRAM_NAME,
            "update",
            *[os.path.relpath(file.path) for file, _ in differing_files],
        ]

        if args.languages:
            command.extend(["--languages", " ".join(args.languages)])

        print(
            f"To merge the settings and extensions, run: {shlex.join(command)}",
            file=sys.stderr,
        )

        return 1
