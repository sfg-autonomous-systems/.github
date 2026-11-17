from __future__ import annotations

import shlex
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from sfg_contribution_tooling import constants, files
from sfg_contribution_tooling.commands.command import Command
from sfg_contribution_tooling.configuration_files import ConfigurationFiles
from sfg_contribution_tooling.error import Error
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
    usage = "%(prog)s [-h] [directory] [--languages LANGUAGE ...]"
    description = textwrap.dedent("""\
        Copy the configuration files of the chosen languages into the directory and
        create .vscode/settings.json and .vscode/extensions.json. Set up all
        languages unless --languages is given.

        Existing files are never changed, only checked. For a configuration file
        that differs, a warning names the reference to compare it with. For VS Code
        files that differ, the update command to run is printed, and the exit
        status is 1.

        After creating .vscode/extensions.json, offer to install the extensions.
    """)
    examples = (f"{constants.PROGRAM_NAME} init --languages python markdown",)
    languages_help = "languages to set up"

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "directory",
            nargs="?",
            default=".",
            help="repository root (default: current directory)",
        )

    def run(self, args: argparse.Namespace, setups: LanguageSetups) -> int:
        directory = Path(args.directory)

        if not directory.is_dir():
            raise Error(f"{files.display(directory)}: not a directory")

        selected = setups.select(args.languages)
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
            differences = file.differences_from(vscode)

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
            *[files.display(file.path) for file, _ in differing_files],
        ]

        if args.languages:
            command.extend(["--languages", *dict.fromkeys(args.languages)])

        print(
            f"To merge the settings and extensions, run: {shlex.join(command)}",
            file=sys.stderr,
        )

        return 1
