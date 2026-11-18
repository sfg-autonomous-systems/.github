from __future__ import annotations

from pathlib import Path

PROGRAM_NAME = "sfg-contribution-tooling"

# The build script replaces the placeholder with the version of the package.
VERSION = "0.0.0"

# The package is installed to <prefix>/lib/sfg_contribution_tooling.
INSTALL_PREFIX = Path(__file__).resolve().parents[2]
LANGUAGE_SETUPS_FILE = INSTALL_PREFIX / "share" / "language-setups.jsonc"
CONFIG_DIRECTORY = INSTALL_PREFIX / "share" / "config"
DPRINT_BINARY = INSTALL_PREFIX / "bin" / "dprint"
