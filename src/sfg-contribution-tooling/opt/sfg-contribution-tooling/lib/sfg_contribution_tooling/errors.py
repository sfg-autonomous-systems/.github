from __future__ import annotations


class Error(Exception):
    """An error that ends the command with a message instead of a traceback."""


class UnexpectedTypeError(Error):
    """A section or one of its parents has the wrong JSON type, such as '"customizations": []'."""
