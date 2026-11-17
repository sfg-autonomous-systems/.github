"""Set up a repository for the SFG Autonomous Systems contribution guidelines in VS Code."""

from __future__ import annotations

import argparse
import io
import sys

from sfg_contribution_tooling import constants
from sfg_contribution_tooling.commands.command import Command
from sfg_contribution_tooling.commands.init_command import InitCommand
from sfg_contribution_tooling.commands.update_command import UpdateCommand
from sfg_contribution_tooling.error import Error
from sfg_contribution_tooling.language_setups import LanguageSetups


def create_parser(setups: LanguageSetups) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=constants.PROGRAM_NAME, description=__doc__)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {constants.VERSION}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in (InitCommand(setups), UpdateCommand(setups)):
        command.register_with(subparsers)

    return parser


def main() -> int:
    # Keeps the order of stdout and stderr in logs, where stdout is not a terminal.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

    try:
        setups = LanguageSetups.read(constants.LANGUAGE_SETUPS_FILE)
        args = create_parser(setups).parse_args()
        command: Command = args.selected_command
        return command.run(args)
    except Error as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
