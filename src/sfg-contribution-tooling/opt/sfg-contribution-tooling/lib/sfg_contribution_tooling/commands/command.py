from __future__ import annotations

import abc
import argparse
import shutil
import textwrap
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from sfg_contribution_tooling.language_setups import LanguageSetups


class Command(abc.ABC):
    """A command of the command line interface with its arguments and help."""

    name: ClassVar[str]
    help: ClassVar[str]
    usage: ClassVar[str]
    description: ClassVar[str]
    examples: ClassVar[tuple[str, ...]]

    # The help of the --languages option before the note on its values.
    languages_help: ClassVar[str]

    class HelpFormatter(argparse.RawDescriptionHelpFormatter):
        """Keeps the line breaks of descriptions and examples, which are wrapped to 80 columns.

        The help of the arguments is wrapped to the same width, as argparse otherwise fills the
        whole terminal with it.
        """

        def __init__(self, prog: str) -> None:
            super().__init__(
                prog, width=min(shutil.get_terminal_size().columns - 2, 79)
            )

    def add_parser(
        self,
        subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
        language_keys: list[str],
    ) -> None:
        """Add the parser of the command, which runs the command, to the subparsers."""
        # Lists the languages in the epilog, as the help of an option breaks 'github-actions' apart.
        languages_epilog = "languages:\n" + textwrap.fill(
            ", ".join(language_keys),
            width=79,
            initial_indent="  ",
            subsequent_indent="  ",
            break_on_hyphens=False,
        )
        examples_heading = "example:" if len(self.examples) == 1 else "examples:"
        parser = subparsers.add_parser(
            self.name,
            usage=self.usage,
            help=self.help,
            formatter_class=Command.HelpFormatter,
            description=self.description,
            epilog=f"{languages_epilog}\n\n{examples_heading}\n"
            + "".join(f"  {example}\n" for example in self.examples),
        )

        # Added before the arguments of the command, so it comes first among the options.
        parser.add_argument(
            "--languages",
            nargs="+",
            choices=language_keys,
            metavar="LANGUAGE",
            help=f"{self.languages_help} (default: all); takes all following values, "
            "so give it after the positional arguments",
        )
        self._add_arguments(parser)
        parser.set_defaults(selected_command=self)

    @abc.abstractmethod
    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add the arguments of the command other than --languages."""

    @abc.abstractmethod
    def run(self, args: argparse.Namespace, setups: LanguageSetups) -> int:
        """Run the command and return its exit status."""
