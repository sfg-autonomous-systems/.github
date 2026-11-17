from __future__ import annotations

import abc
import argparse
import shutil
import textwrap
from typing import ClassVar


class Command(abc.ABC):
    """A command of the command line interface with its arguments and help."""

    name: ClassVar[str]
    help: ClassVar[str]
    description: ClassVar[str]

    class HelpFormatter(argparse.RawDescriptionHelpFormatter):
        """Keeps the line breaks of descriptions, which are written for 80 columns.

        The help of the arguments is wrapped to the same width, as argparse otherwise fills the
        whole terminal with it.
        """

        def __init__(self, prog: str) -> None:
            super().__init__(
                prog, width=min(shutil.get_terminal_size().columns - 2, 79)
            )

        def _split_lines(self, text: str, width: int) -> list[str]:
            # Like argparse, but keeps names such as 'github-actions' on one line.
            text = self._whitespace_matcher.sub(" ", text).strip()
            return textwrap.wrap(text, width, break_on_hyphens=False)

    @abc.abstractmethod
    def run(self, args: argparse.Namespace) -> int:
        """Run the command and return its exit status."""

    def register_with(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        """Add a parser for the command to the subparsers, which selects it by its name."""
        parser = subparsers.add_parser(
            self.name,
            help=self.help,
            description=self.description,
            formatter_class=Command.HelpFormatter,
        )
        self._add_arguments(parser)

        # Puts the command into the parsed arguments, so main runs it without a branch per command.
        parser.set_defaults(selected_command=self)

    @staticmethod
    def _add_languages_argument(
        parser: argparse.ArgumentParser, language_keys: list[str], help_text: str
    ) -> None:
        """Add the --languages option, which takes the languages as one value separated by spaces.

        The parsed value is the list of chosen keys without duplicates, or None if none are given.
        """

        def parse_languages(value: str) -> list[str]:
            keys = list(dict.fromkeys(value.split()))

            if not keys:
                raise argparse.ArgumentTypeError("expected at least one language")

            unknown = [key for key in keys if key not in language_keys]

            if unknown:
                raise argparse.ArgumentTypeError(
                    f"unknown {'language' if len(unknown) == 1 else 'languages'} "
                    f"{', '.join(unknown)} (choose from {', '.join(language_keys)})"
                )

            return keys

        parser.add_argument(
            "--languages",
            type=parse_languages,
            metavar='"LANGUAGE ..."',
            help=f"{help_text}, separated by spaces (default: all): {', '.join(language_keys)}",
        )

    @abc.abstractmethod
    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add the arguments of the command."""
