from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from sfg_contribution_tooling.errors import Error

if TYPE_CHECKING:
    from sfg_contribution_tooling.vscode.vscode_setup import VsCodeSetup


class ExtensionInstaller:
    """Offers to install the missing extensions of a VS Code setup."""

    def __init__(self, vscode_setup: VsCodeSetup) -> None:
        self.vscode_setup = vscode_setup

    def offer(self) -> None:
        """Install the missing extensions with 'code', after asking.

        Raises:
            Error: If installing the extensions fails.
        """
        code = shutil.which("code")

        if code is None:
            print("Install the recommended extensions from VS Code.")
            return

        installed = self._get_installed_extensions(code)
        extensions = [
            extension
            for extension in self.vscode_setup.extensions
            if extension.lower() not in installed
        ]

        if not extensions:
            return

        command = ["code"]

        for extension in extensions:
            command.extend(["--install-extension", extension])

        # Never install without asking. Give non-interactive sessions only the command.
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
    def _get_installed_extensions(code: str) -> set[str]:
        """Return the installed extension IDs in lowercase, empty if retrieval fails.

        Args:
            code: Path of the 'code' executable.

        Returns:
            The IDs, or an empty set if 'code' cannot be run or fails.
        """
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
