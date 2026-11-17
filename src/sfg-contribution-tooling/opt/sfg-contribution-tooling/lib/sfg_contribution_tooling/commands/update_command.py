from __future__ import annotations

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from sfg_contribution_tooling import constants
from sfg_contribution_tooling.commands.command import Command
from sfg_contribution_tooling.vscode.extension_installer import ExtensionInstaller
from sfg_contribution_tooling.vscode.file_kind import FileKind
from sfg_contribution_tooling.vscode.vscode_file import VsCodeFile
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup

if TYPE_CHECKING:
    import argparse

    from sfg_contribution_tooling.language_setups import LanguageSetups


class UpdateCommand(Command):
    """Merges the settings and extensions into existing VS Code files, or only checks them."""

    name = "update"
    help = "merge the settings and extensions into existing VS Code files"
    # Wrapped like argparse wraps a generated usage, which it does not do for a given one.
    usage = (
        "%(prog)s [-h] FILE ... [--languages LANGUAGE ...]\n"
        + " " * len(f"usage: {constants.PROGRAM_NAME} update ")
        + "[--check]"
    )
    description = textwrap.dedent("""\
        Merge the settings and extensions of the chosen languages into existing
        settings.json, extensions.json and devcontainer.json files. Merge those of
        all languages unless --languages is given.

        Changed files lose their comments, run with --check first to list the
        differences without writing anything.

        After updating an extensions.json, offer to install the extensions.
    """)
    examples = (
        f"{constants.PROGRAM_NAME} update .devcontainer/devcontainer.json --check",
        f"{constants.PROGRAM_NAME} update .devcontainer/devcontainer.json",
    )
    languages_help = "languages whose settings and extensions are merged"

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "files",
            nargs="+",
            metavar="FILE",
            help="settings.json, extensions.json, devcontainer.json or .devcontainer.json file",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="only list the differences and exit with status 1 if there are any",
        )

    def run(self, args: argparse.Namespace, setups: LanguageSetups) -> int:
        vscode = VsCodeSetup.combine(setups.select(args.languages))
        unique_paths: dict[Path, Path] = {}

        for file in args.files:
            unique_paths.setdefault(Path(file).resolve(), Path(file))

        paths = list(unique_paths.values())

        for path in paths:
            FileKind.from_path(path)

        changed_files: list[VsCodeFile] = []
        has_differences = False

        # Loads and merges every file before writing any, so a failure leaves all unchanged.
        for path in paths:
            file = VsCodeFile.load(path)
            differences = file.differences_from(vscode)

            if not differences:
                continue

            has_differences = True

            if args.check:
                file.report(differences)
                continue

            file.merge_from(vscode)
            changed_files.append(file)

        if args.check:
            return 1 if has_differences else 0

        for file in changed_files:
            file.write()

        # The Dev Containers extension installs the extensions of a devcontainer.json itself.
        if any(file.kind is FileKind.Extensions for file in changed_files):
            ExtensionInstaller(vscode).offer()

        return 0
