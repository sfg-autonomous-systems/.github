from __future__ import annotations

from sfg_contribution_tooling.error import Error


class UnexpectedTypeError(Error):
    """A section or one of its parents has the wrong JSON type, such as '"customizations": []'."""
