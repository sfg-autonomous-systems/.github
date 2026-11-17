from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from sfg_contribution_tooling.error import Error

if TYPE_CHECKING:
    from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


class ExtensionInstaller:
    """Offers to install the extensions of a VS Code setup that are not installed yet."""

    def __init__(self, setup: VsCodeSetup) -> None:
        self.setup = setup

    def offer(self) -> None:
        """Install the extensions that are not installed yet with 'code', after asking."""
        code = shutil.which("code")

        if code is None:
            print("Install the recommended extensions from VS Code.")
            return

        installed = self._list_installed_extensions(code)
        extensions = [
            extension
            for extension in self.setup.extensions
            if extension.lower() not in installed
        ]

        if not extensions:
            return

        command = ["code"]

        for extension in extensions:
            command.extend(["--install-extension", extension])

        # Never installs without asking, so a CI job or a 'postCreateCommand' only gets the command.
        if not sys.stdin.isatty():
            print(f"To install the extensions, run: {shlex.join(command)}")
            return

        try:
            answer = input(
                f"Install {', '.join(extensions)} with 'code --install-extension'? [y/N] "
            )
        except (EOFError, KeyboardInterrupt):
            print()
            answer = ""

        if answer.strip().lower() not in ("y", "yes"):
            return

        if subprocess.run([code, *command[1:]], check=False).returncode != 0:
            raise Error("installing the extensions failed")

    @staticmethod
    def _list_installed_extensions(code: str) -> set[str]:
        """Return the lowercase IDs of the installed extensions, or none if 'code' cannot list them."""
        try:
            result = subprocess.run(
                [code, "--list-extensions"],
                capture_output=True,
                encoding="utf-8",
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return set()

        return {line.strip().lower() for line in result.stdout.splitlines()}
