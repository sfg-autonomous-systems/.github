from __future__ import annotations

import json
import re
from typing import Any

from sfg_contribution_tooling.errors import Error

_INDENT = "    "

# Whitespace up to a closing brace or bracket,
# which makes a preceding comma a trailing one.
_CLOSING_PATTERN = re.compile(r"\s*[}\]]")


def _find_string_end(text: str, start: int) -> int:
    """Return the index after the string that starts with the quote at 'start'.

    Args:
        text: Text containing the string.
        start: Index of the opening quote.

    Returns:
        The index after the closing quote, or an index past the end of the text if the
        string is not terminated.
    """
    index = start + 1

    # Skips escaped characters, so an escaped quote does not end the string.
    while index < len(text) and text[index] != '"':
        index += 2 if text[index] == "\\" else 1

    return index + 1


def parse(text: str) -> tuple[Any, bool]:
    """Parse JSON with comments and trailing commas, as VS Code allows.

    Comments and trailing commas are replaced by spaces, so the positions in parse
    errors stay correct.

    Args:
        text: Text to parse. A leading byte order mark is ignored.

    Returns:
        The value and whether the text had comments.

    Raises:
        Error: If a block comment is not terminated or the text is not valid JSON. The
            error does not name the file; the caller adds it.
    """
    text = text.removeprefix("\N{BYTE ORDER MARK}")
    characters = list(text)
    has_comments = False
    index = 0

    while index < len(text):
        if text[index] == '"':
            index = _find_string_end(text, index)
            continue

        if text.startswith("//", index):
            end = text.find("\n", index)
            end = len(text) if end == -1 else end
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)

            if end == -1:
                raise Error("unterminated comment")

            end += 2
        else:
            index += 1
            continue

        # Keeps the line breaks of block comments.
        for position in range(index, end):
            if characters[position] != "\n":
                characters[position] = " "

        has_comments = True
        index = end

    text = "".join(characters)
    index = 0

    # Removes trailing commas in a second pass, as
    # a comment may precede the closing bracket.
    while index < len(text):
        if text[index] == '"':
            index = _find_string_end(text, index)
            continue

        if text[index] == "," and _CLOSING_PATTERN.match(text, index + 1):
            characters[index] = " "

        index += 1

    try:
        return json.loads("".join(characters)), has_comments
    except json.JSONDecodeError as error:
        raise Error(f"cannot be parsed: {error}") from None


def dump(value: Any, level: int = 0, comments: dict[str, str] | None = None) -> str:
    """Serialize a value with one line per object property.

    dprint keeps objects on one line if they start on one line, but wraps arrays that
    are too long, so only arrays are written on one line.

    Args:
        value: JSON value to serialize.
        level: Nesting depth of the value, which sets the indentation of its lines.
        comments: Comments to write above properties of the value, by property key.
            Properties of nested objects get no comments.

    Returns:
        The serialized value, without a trailing line break.
    """
    if isinstance(value, dict) and value:
        indent = _INDENT * (level + 1)
        properties = []

        for key, item in value.items():
            comment = (
                f"{indent}// {comments[key]}\n" if comments and key in comments else ""
            )
            properties.append(
                f"{comment}{indent}{format_value(key)}: {dump(item, level + 1)}"
            )

        return "{\n" + ",\n".join(properties) + f"\n{_INDENT * level}}}"

    return format_value(value)


def format_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def are_equal(first: Any, second: Any) -> bool:
    """Compare two JSON values, telling apart values Python considers equal.

    Args:
        first: One value.
        second: The other value.

    Returns:
        Whether the values serialize the same, ignoring the order of object keys.
    """
    return json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def describe_type(value: Any) -> str:
    match value:
        case dict():
            return "an object"
        case list():
            return "an array"
        case str():
            return "a string"
        case bool():
            return "a boolean"
        case None:
            return "null"
        case _:
            return "a number"


def format_key_path(key_path: tuple[str, ...]) -> str:
    return ".".join(key_path)
