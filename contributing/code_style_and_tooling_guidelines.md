# Code Style & Tooling Guidelines

This document outlines the shared tooling and editor configuration for our development, and links to the per-language style guidelines.

## Tooling & Editor Configuration

We use **[Visual Studio Code](https://code.visualstudio.com/)** as our primary IDE. To ensure everyone's code is formatted identically and automatically upon saving, you must apply the settings below.

### Tools

All formatters and linters come in the `sfg-contribution-tooling` package. [Add the SFG APT repository](https://github.com/sfg-autonomous-systems/sfg_apt_repo#add-the-apt-repository), then install the package:

```bash
sudo apt install sfg-contribution-tooling
```

The package installs `clang-format`, `ruff`, `shellcheck`, `shfmt` and `ty` to `/opt/sfg-contribution-tooling/bin/`, which is not on the `PATH`, and the configuration files from [`config/`](config/) to `/opt/sfg-contribution-tooling/share/config/`.

### Editor & Repository Setup

For each language the repository uses, install the extensions and copy the configuration files from [`config/`](config/) into the repository root:

| Language | Extensions                                                                        | Configuration Files                                                              | Style Guidelines          |
| -------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------- |
| C++      | [`ms-vscode.cpptools`][cpptools], [`josetr.cmake-language-support-vscode`][cmake] | [`.clang-format`](config/.clang-format)                                          | [C++](style/cpp.md)       |
| Shell    | [`mads-hartmann.bash-ide-vscode`][bash-ide]                                       | [`.editorconfig`](config/.editorconfig), [`.shellcheckrc`](config/.shellcheckrc) | [Shell](style/shell.md)   |
| Python   | [`ms-python.python`][python], [`charliermarsh.ruff`][ruff], [`astral-sh.ty`][ty]  | [`ruff.toml`](config/ruff.toml), [`ty.toml`](config/ty.toml)                     | [Python](style/python.md) |

[cpptools]: https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools
[cmake]: https://marketplace.visualstudio.com/items?itemName=josetr.cmake-language-support-vscode
[bash-ide]: https://marketplace.visualstudio.com/items?itemName=mads-hartmann.bash-ide-vscode
[python]: https://marketplace.visualstudio.com/items?itemName=ms-python.python
[ruff]: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff
[ty]: https://marketplace.visualstudio.com/items?itemName=astral-sh.ty

Then add the following to the repository's `.vscode/settings.json`. Use the whole block in every repository. Settings for languages and extensions a repository does not use are ignored.

```json
{
    "editor.formatOnSave": true,
    "C_Cpp.clang_format_path": "/opt/sfg-contribution-tooling/bin/clang-format",
    "bashIde.shellcheckPath": "/opt/sfg-contribution-tooling/bin/shellcheck",
    "bashIde.shfmt.path": "/opt/sfg-contribution-tooling/bin/shfmt",
    "python.languageServer": "Pylance",
    "ruff.path": ["/opt/sfg-contribution-tooling/bin/ruff"],
    "ty.path": ["/opt/sfg-contribution-tooling/bin/ty"],
    "ty.disableLanguageServices": true,
    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools"
    },
    "[cmake]": {
        "editor.defaultFormatter": "josetr.cmake-language-support-vscode"
    },
    "[shellscript]": {
        "editor.defaultFormatter": "mads-hartmann.bash-ide-vscode",
        "editor.detectIndentation": false,
        "editor.insertSpaces": true,
        "editor.tabSize": 4
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

> [!warning]
> ty and Bash IDE look for `ty.toml` and `.shellcheckrc` only in the VS Code workspace directory and its parent directories. Open the repository root as the workspace. If you open a parent directory, also copy `.shellcheckrc` to `~/.config/shellcheckrc`.

> [!warning]
> Configure each tool in exactly one place. Do not additionally add `[tool.ruff]` or `[tool.ty]` sections to a `pyproject.toml`: `ruff.toml` and `ty.toml` take precedence and such sections are ignored.
