from __future__ import annotations

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from sfg_contribution_tooling.commands.command import Command
from sfg_contribution_tooling.vscode.extension_installer import ExtensionInstaller
from sfg_contribution_tooling.vscode.file_kind import FileKind
from sfg_contribution_tooling.vscode.vscode_file import VsCodeFile
from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup

if TYPE_CHECKING:
    import argparse

    from sfg_contribution_tooling.language_setups import LanguageSetups


class UpdateCommand(Command):
    """Merges the settings and extensions into VS Code files, or only checks them."""

    name = "update"
    help = "merge the settings and extensions into existing VS Code files"
    description = textwrap.dedent("""\
        Merges the settings and extensions of the chosen languages into existing
        settings.json, extensions.json and devcontainer.json files. Merges those of
        all languages unless --languages is given.

        Changed files lose their comments. Running with --check first lists the
        differences without writing anything.

        After updating an extensions.json, offers to install the extensions.
    """)

    def __init__(self, language_setups: LanguageSetups) -> None:
        self._language_setups = language_setups

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "files",
            nargs="+",
            metavar="FILE",
            help="settings.json, extensions.json, devcontainer.json or .devcontainer.json file",
        )
        self._add_languages_argument(
            parser,
            self._language_setups.get_selectable_keys(),
            "languages whose settings and extensions are merged",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="only list the differences and exit with status 1 if there are any",
        )

    def run(self, args: argparse.Namespace) -> int:
        vscode = VsCodeSetup.combine(self._language_setups.select(args.languages))
        unique_filepaths: dict[Path, Path] = {}

        for file in args.files:
            unique_filepaths.setdefault(Path(file).resolve(), Path(file))

        filepaths = list(unique_filepaths.values())

        for filepath in filepaths:
            FileKind.from_path(filepath)

        changed_files: list[VsCodeFile] = []
        has_differences = False

        # Loads and merges every file before writing any, so a failure leaves all
        # unchanged.
        for filepath in filepaths:
            file = VsCodeFile.load(filepath)
            differences = file.find_differences(vscode)

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

        # The Dev Containers extension installs the extensions of a devcontainer.json
        # itself.
        if any(file.kind is FileKind.Extensions for file in changed_files):
            ExtensionInstaller(vscode).offer()

        return 0
