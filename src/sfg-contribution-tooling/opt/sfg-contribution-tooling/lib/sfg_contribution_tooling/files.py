from __future__ import annotations

import os
from pathlib import Path

from sfg_contribution_tooling.errors import Error


def describe_error(error: Exception) -> str:
    """Return the reason of a file error without the path, which the message already names."""
    if isinstance(error, OSError) and error.strerror:
        return error.strerror

    return str(error)


def read_bytes(filepath: Path) -> bytes:
    try:
        return filepath.read_bytes()
    except OSError as error:
        raise Error(f"{os.path.relpath(filepath)}: {describe_error(error)}") from None


def read_text(filepath: Path) -> str:
    try:
        return filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise Error(f"{os.path.relpath(filepath)}: {describe_error(error)}") from None


def write(filepath: Path, content: str | bytes, verb: str, note: str = "") -> None:
    """Write the file, creating its directory, and print a line starting with 'verb' for it."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            filepath.write_bytes(content)
        else:
            filepath.write_text(content, encoding="utf-8")
    except OSError as error:
        raise Error(f"{os.path.relpath(filepath)}: {describe_error(error)}") from None

    print(f"{verb} {os.path.relpath(filepath)}{note}")
